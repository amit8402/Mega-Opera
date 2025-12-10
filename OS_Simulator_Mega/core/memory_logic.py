# core/memory_logic.py
import math
import random

class MemoryManager:
    """
    Supports:
     - Paging: fixed-size frames
     - Segmentation: variable-size segments with first/best/worst fit
    """

    def __init__(self, total_kb=1000, frame_kb=10):
        self.total_kb = total_kb
        self.frame_kb = frame_kb
        self.num_frames = self.total_kb // self.frame_kb
        # Paging state
        self.frames = [None] * self.num_frames          # each entry = process name or None
        self.page_table = {}                             # process -> list of frame indices

        # Segmentation state
        # segments = list of dict { process, seg_id, start_kb, size_kb }
        self.segments = []
        # free blocks list for segmentation as (start_kb, size_kb)
        self.free_blocks = [(0, self.total_kb)]

    # ---------------- PAGING ----------------
    def allocate_paging(self, process, size_kb):
        pages_needed = math.ceil(size_kb / self.frame_kb)
        free_indices = [i for i, v in enumerate(self.frames) if v is None]
        if len(free_indices) < pages_needed:
            return False, "Not enough free frames"

        allocated = free_indices[:pages_needed]
        for i in allocated:
            self.frames[i] = process
        self.page_table[process] = allocated
        return True, allocated

    def free_paging(self, process):
        if process in self.page_table:
            for i in self.page_table[process]:
                if 0 <= i < len(self.frames):
                    self.frames[i] = None
            del self.page_table[process]
            return True
        # fallback: scan frames and free
        freed = False
        for i, p in enumerate(self.frames):
            if p == process:
                self.frames[i] = None
                freed = True
        if freed:
            self.rebuild_page_table()
            return True
        return False

    def rebuild_page_table(self):
        self.page_table = {}
        for idx, p in enumerate(self.frames):
            if p is not None:
                self.page_table.setdefault(p, []).append(idx)

    def get_paging_state(self):
        return {
            "frames": list(self.frames),
            "page_table": dict(self.page_table),
            "num_frames": self.num_frames,
            "frame_kb": self.frame_kb
        }

    # ---------------- SEGMENTATION ----------------
    def allocate_segment(self, process, seg_size_kb, policy="first"):
        """
        Try to allocate a contiguous block of size seg_size_kb using policy:
         - 'first' : first-fit
         - 'best'  : best-fit
         - 'worst' : worst-fit
        Returns (True, start_kb) or (False, reason)
        """
        # refresh free_blocks by merging contiguous
        self._merge_free_blocks()

        candidate_index = None
        if policy == "first":
            for idx, (start, size) in enumerate(self.free_blocks):
                if size >= seg_size_kb:
                    candidate_index = idx
                    break
        elif policy == "best":
            best_idx = None
            best_size = None
            for idx, (start, size) in enumerate(self.free_blocks):
                if size >= seg_size_kb:
                    if best_size is None or size < best_size:
                        best_size = size
                        best_idx = idx
            candidate_index = best_idx
        elif policy == "worst":
            worst_idx = None
            worst_size = -1
            for idx, (start, size) in enumerate(self.free_blocks):
                if size >= seg_size_kb and size > worst_size:
                    worst_size = size
                    worst_idx = idx
            candidate_index = worst_idx
        else:
            return False, "Unknown policy"

        if candidate_index is None:
            return False, "No contiguous block large enough (external fragmentation?)"

        start, size = self.free_blocks.pop(candidate_index)
        allocated_start = start
        leftover = size - seg_size_kb
        if leftover > 0:
            self.free_blocks.insert(candidate_index, (start + seg_size_kb, leftover))

        seg_id = f"{process}_S{len([s for s in self.segments if s['process']==process])+1}"
        seg = {
            "process": process,
            "seg_id": seg_id,
            "start_kb": allocated_start,
            "size_kb": seg_size_kb
        }
        self.segments.append(seg)
        # sort segments by start for clarity
        self.segments.sort(key=lambda s: s["start_kb"])
        return True, seg

    def free_segments_of(self, process):
        removed = [s for s in self.segments if s["process"] == process]
        if not removed:
            return False
        # free blocks
        for s in removed:
            self.free_blocks.append((s["start_kb"], s["size_kb"]))
        # remove segments
        self.segments = [s for s in self.segments if s["process"] != process]
        self._merge_free_blocks()
        return True

    def _merge_free_blocks(self):
        """merge free_blocks contiguous and sort"""
        fb = sorted(self.free_blocks, key=lambda x: x[0])
        merged = []
        for start, size in fb:
            if not merged:
                merged.append((start, size))
            else:
                last_start, last_size = merged[-1]
                if last_start + last_size == start:
                    merged[-1] = (last_start, last_size + size)
                else:
                    merged.append((start, size))
        self.free_blocks = merged

    def get_segmentation_state(self):
        return {
            "segments": list(self.segments),
            "free_blocks": list(self.free_blocks),
            "total_kb": self.total_kb
        }

    # ---------------- misc helpers ----------------
    def reset(self):
        self.frames = [None] * self.num_frames
        self.page_table.clear()
        self.segments.clear()
        self.free_blocks = [(0, self.total_kb)]
