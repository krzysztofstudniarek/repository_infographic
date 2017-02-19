from mako.template import Template

mytemplate = Template(filename='template.html')
print(mytemplate.render(name = "ala ma kota"))