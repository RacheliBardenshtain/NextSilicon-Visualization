from PyQt5.QtWidgets import QMessageBox
from utils.filter_types import FILTER_TYPES_NAMES, TIMERANGE, TIME
from utils.type_names import AREAS, UNITS
from entities.filter import Filter
from utils.filter_types import IO, CLUSTER, QUAD, THREADID, AREA, UNIT

class FilterManager:
    def __init__(self, parent=None):
        # Store active filters and their values
        self.active_filters = {}  # key: filter type, value: (filter_name, current_value)
        self.value_options = {
            FILTER_TYPES_NAMES[IO]: {'in/out': ['in', 'out']},
            FILTER_TYPES_NAMES[CLUSTER]: {'chip': ['0'], 'die': ['DIE1', 'DIE2'], 'quad': ['NW', 'NE', 'SW', 'SE'], 'row': [str(row) for row in range(8)], 'column': [str(row) for row in range(8)]},
            FILTER_TYPES_NAMES[QUAD]: {'chip': ['0'], 'die': ['DIE1', 'DIE2'], 'quad': ['HW', 'NE', 'SW', 'SE']},
            FILTER_TYPES_NAMES[THREADID]: {'TID': []},
            FILTER_TYPES_NAMES[AREA]: {'Area': list(AREAS.keys())},
            FILTER_TYPES_NAMES[UNIT]: {'Unit': UNITS}
        }
        self.filters = {}
        self.construction_of_filters()
        self.parent = parent

    def construction_of_filters(self):
        for filter_type in FILTER_TYPES_NAMES:
            if filter_type != TIME and filter_type != TIMERANGE:
                filter = Filter(filter_type, self.value_options[filter_type])
                self.filters[filter_type] = filter

    def remove_tid(self, tid):
        tid = int(tid)
        if tid in self.filters['ThreadId'].values:
            self.filters['ThreadId'].values.remove(tid)
        else:
            QMessageBox.warning(self, "Warning", f"TID {tid} not found in the list.")

        if self.filters['ThreadId'].values == []:
            self.remove_filter("ThreadId")
        else:
            self.parent.parent.update_filter_in_chain("ThreadId", self.filters['ThreadId'].values)

    def apply_filter(self, filter_type: str) -> None:
        """Apply the filter with the given name and values."""
        values_dict = self.filters[filter_type].ready_for_filter
        print(values_dict)
        if not filter_type == 'ThreadId':
            values = list(values_dict.values())
        else:
            values = values_dict
        if len(values) == 1 and not filter_type == 'ThreadId':
            values = values[0]
        print(f'Filter {filter_type} applied with values: {values}')
        if self.parent.parent is not None or (filter_type == 'ThreadId' and self.filters['ThreadId'].values == []):
            if self.filters[filter_type].is_active:
                self.parent.parent.update_filter_in_chain(filter_type, values)
            else:
                self.filters[filter_type].is_active = True
                print(self.parent)
                self.parent.update_filter_Text()
                self.parent.parent.change_filter(filter_type, values)

    def clear_all_filters(self) -> None:
        """Clear all selected filters and update the menu."""
        self.filters['ThreadId'].values = []
        for filter_type, filter in self.filters.items():
            filter.is_active = False

        self.parent.update_filter_Text()
        self.parent.parent.clear_all_filters()

    def remove_filter(self, filter_type: str) -> None:
        """Remove a specific filter and update the menu."""
        self.parent.close()
        if filter_type == 'ThreadId':
            self.filters['ThreadId'].values = []
        if self.filters[filter_type].is_active:
            self.filters[filter_type].is_active = False
            self.parent.update_filter_Text()
            self.parent.parent.filter_removal(filter_type)
