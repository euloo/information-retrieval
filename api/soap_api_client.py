from zeep import Client
#from lxml import etree as ET

client = Client('http://localhost:5000/?wsdl')
print(client.service.get_movies())
print(client.service.get_movie('0000000'))
print(client.service.get_movie_by(2010))
print(client.service.get_movie_by(2010, 'Documentary'))
print(client.service.get_movie_by(genre='Documentary'))
print(client.service.add_movie('0000000', 'Test'))
print(client.service.update_movie('0000000', 'TEST'))
print(client.service.delete_movie('0000000'))

#node=client.create_message(client.service, 'Insoap', movie_id='0000000')
#tree = ET.ElementTree(node)
#tree.write('test.xml',pretty_print=True)

#import requests
#
#xml="""<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
#  <soap-env:Body>
#    <ns0:Insoap xmlns:ns0="Movie">
#      <ns0:movie_id>0000000</ns0:movie_id>
#    </ns0:Insoap>
#  </soap-env:Body>
#</soap-env:Envelope>
#"""
#
#res=requests.post('http://localhost:5000',data=xml, headers={'Content-Type': 'application/xml'})
#print(res.text)