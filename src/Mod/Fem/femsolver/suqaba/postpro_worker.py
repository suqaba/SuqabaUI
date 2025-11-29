import os
import sys
import json
import FreeCAD


def run_postpro(working_dir, case_name, request):
    doc = FreeCAD.newDocument()
    obj = doc.addObject("Fem::SuqabaPostpro")
    obj.WorkingDir = working_dir
    obj.CaseName = case_name
    obj.setPostproRequest(request)
    obj.run()
    doc.removeObject(obj.Name)


working_dir = sys.argv[2]
case_name   = sys.argv[3]
request     = json.loads(sys.argv[4])

run_postpro(working_dir, case_name, request)

os._exit(0)
