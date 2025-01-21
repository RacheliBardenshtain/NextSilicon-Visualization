class Filter:
    def __init__(self,type_name,value_options):
        self.type_name: type_name
        self.is_active = False
        self.value_options = value_options
        self.values = []
        self.ready_for_filter=[]





