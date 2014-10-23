from lxml import etree
import sys

TAGfile = open(sys.argv[1]+"/Testing/TAG", 'r')
dirname = TAGfile.readline().strip()

xmlfile = sys.argv[1]+"/Testing/"+dirname+"/Test.xml"
xslfile = sys.argv[2]

xmldoc = etree.parse(xmlfile)
xslt_root = etree.parse(xslfile)
transform = etree.XSLT(xslt_root)

result_tree = transform(xmldoc)
print(result_tree)
