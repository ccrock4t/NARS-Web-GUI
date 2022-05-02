# These keys are only used in the communication between NARS and the server
# the server uses these as a common language to interface with NARS

# Commands sent to GUI from NARS
PATH_INITIALIZE = "/Initialize/"
PATH_ADD_CONCEPT = "/AddConcept/"
PATH_SHOW_CONCEPT_INFO = "/ShowConceptInfo/"
PATH_ADD_LINK = "/AddLink/"
PATH_ADD_TASK_TO_BUFFER = "/AddTaskToBuffer/"
PATH_REMOVE_TASK_FROM_BUFFER = "/RemoveTaskFromBuffer/"

# Commands sent to NARS from GUI
COMMAND = "COMMAND"
COMMAND_INPUT = "INPUT"
COMMAND_GET_CONCEPT_INFO = "GET_CONCEPT_INFO"

KEY_NARS_NAME = "NARS_name"
KEY_BUFFERS = "buffers"
KEY_BUFFER_NAME = "buffer_name"
KEY_BUFFER_CAPACITY = "buffer_capacity"
KEY_SENTENCE = "sentence"
KEY_BUDGET = "budget"
KEY_SENTENCE_ID = "sentence_ID"

KEY_CONCEPT_ID = "concept_ID"
KEY_TERM_TYPE = "term_type"
KEY_TERM_TYPE_ATOMIC = "atomic"
KEY_TERM_TYPE_STATEMENT = "statement"
KEY_LINK_TYPE = "link_type"
KEY_LINK_TYPE_TERMLINK = "termlink"
KEY_LINK_SOURCE = "link_source"
KEY_LINK_TARGET = "link_target"

KEY_DATA = "data"