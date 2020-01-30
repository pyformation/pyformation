def ref(resource, attribute=None):
    if not attribute:
        return {"Ref": resource}
    else:
        return {"Fn::GettAtt": [resource, attribute]}

def caps(resource):
    return "".join([x.capitalize() for x in resource.split('_')])