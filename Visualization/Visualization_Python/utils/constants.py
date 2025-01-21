from PyQt5.QtCore import Qt
from utils.type_names import BMT, H2G, G2H, PCIE, CBU, TCU, ECORE, DIE, QUAD, CBUS_INJ, CBUS_CLT, NFI_INJ, NFI_CLT, EQ, \
    IRQA, IQR, IQD, BIN

CHIP = "chip"
DIES = "DIES"
QUADS = "QUADS"
ECORES = "Ecores"
CBUS = "CBUs"
TCUS = "TCUs"
EQS = "EQs"
ID = "id"
ENABLED_CLUSTERS = "enabled_clusters"
TOP = "Top"
COL = "col"
COLUMN = "Column"
ROW = "row"
DID = "did"
GRID = "GRID"
NAME = "name"
FILTER = "Filter"

CLUSTER_ID = "cluster_id"
TID = "tid"
PACKET = "packet"
UNIT = "unit"
AREA = "area"
TIMESTAMP = "timeStemp"

OBJECT_COLORS = {
    BMT: "lightblue",
    H2G: "pink",
    G2H: "coral",
    PCIE: "yellow",
    CBU: "blue",
    TCU: "red",
    ECORE: "#32CD32",
    DIE: "orange",
    QUAD: "cyan",
    CBUS_INJ: "#4682B4",  # SteelBlue
    CBUS_CLT: "#B0C4DE",  # LightSteelBlue
    NFI_INJ: "#5F9EA0",  # CadetBlue
    NFI_CLT: "#87CEEB",  # SkyBlue
    EQ: "red",
    IRQA: "#AAAAAA",
    IQR: "DeepPink",
    IQD: "coral",
    BIN: "Magenta",
}

SL = "SL"
LOGS = "Logs"
ANIMATION = "Animation"
TOOL_BAR = "toolBar"
OVERLAY = "overlay"

# titles and messages
CLOSE = "Close"
UNKNOWN = "Unknown"
SIMULATOR_INSTRUCTIONS = "Simulator Instructions"
SIMULATOR = "HW Simulator"
MAIN_TOOLBAR = "Main Toolbar"
X_BUTTON = "X"
COMPONENT_LOGS = "{component} Logs"
EMPTY = "Empty"
VIEW_LOGS = "View Logs"
SELECT_REQUIRED_FILES = "Select Required Files"
SELECT_REQUIRED_FILES_MESSAGE = "Please select the required files to continue:"
SL_FILE_MESSAGE = "SL File:  "
CSV_FILE_MESSAGE = "Logs File:"
SELECT_FILE_MESSAGE = "Select {file_name} {type_name} File"
BROWSE = "Browse"
PROCEED = "Proceed"
ENTER_VALUES_FOR_FILTER = "Enter values for {filter_type}"
WAIT_PROCESSING = "Please wait, processing..."
CLIK_FOR_INSTRUCTIONS = "Click for instructions"

# colors
BLACK = "black"
WHITE = "white"
LIGHTGRAY = "lightgray"
GREEN = "green"
RED = "red"
GRAY = "gray"
TRANSPARENT = "transparent"
LIGHTBLUE = "lightblue"

# open_files
READ = "r"
UTF_8 = 'utf-8'

# settings
NUM_QUADS_PER_SIDE = 2
NUM_CLUSTERS_PER_SIDE = 8
NUM_DIES = 2
TYPE_FILE = "{type_file} Files (*{dot_type_file});;All Files (*)"
DOT_JSON = ".json"
DOT_CSV = ".csv"
JSON = "JSON"
CSV = "CSV"

# CURSOR
ARROW_CURSOR = Qt.ArrowCursor
FORBIDDEN_CURSOR = Qt.ForbiddenCursor
POINTING_CURSOR = Qt.PointingHandCursor

# Files in project
MAIN_WINDOW = "Main Window"
FILTER_MENU_WIDGET = "Filter Menu Widget"
HOST_INTERFACE_WIDGET = "Host Interface Widget "
DIE_WIDGET = "Die Widget"
TIME_LINE_WIDGET = "Time Line Widget"
