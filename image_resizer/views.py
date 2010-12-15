from django.core.cache import cache
from google.appengine.api import images
from django.http import HttpResponse
from image_resizer.models import Image
import base64, time
import logging

IMAGE_PREFIX = 'IMAGE_'
CACHE_VERSION_PREFIX="VERSION_"
TIMEOUT=604800 #timeout in 1 week'


def resize(request, image_id):
	if request.method =='GET':
		width =-1
		if request.GET.has_key("width"):
			width = int(request.GET['width'])
		height = -1
		if request.GET.has_key('height'):
			height = int(request.GET['height'])
		logging.debug("width: %s, height: %s" %(width, height))
		version =cache.get("%s_%s" %(CACHE_VERSION_PREFIX, image_id))
		logging.debug("version: %s" %(version))
		if version is None:
			logging.debug("version is none")
			try:
				img =getImage(image_id, width, height)
			except Exception, e:
				logging.debug("Exception caught "+str(e))
				return HttpResponse()
		else:
			image_memcache_key = "%s_%s_%s_%i_%i" %(IMAGE_PREFIX, image_id, version, width, height)
			logging.debug("Image memcache key: %s" %(image_memcache_key))
			img = cache.get(image_memcache_key)
			
			if img is None:
				try:
					logging.debug("Cannot get image")
					img = getImage(image_id, width, height)
				except Exception, e:
					logging.debug("Exception caught "+str(e))
					return HttpResponse()
		logging.debug(img)		
		return HttpResponse(img, mimetype="image/jpg")
		
		
def upload(request):
	if request.method=='POST':
		image_id = request.POST['image_id']
		version = int(time.time())
		try:
			image_byteString = base64.urlsafe_b64decode(request.POST['image_data'].encode('ascii'))
		except e:
			return HttpResponse("{'status':'error'}", mimetype='application/json')
		try:
			image=Image.objects.get(image_id=image_id)
			image.version = version
			image.image_data = image_byteString
		except Image.DoesNotExist, e:
			image = Image(image_id = image_id, version= version, image_data=image_byteString)
			
		image.save()

		cache.set("%s_%s" %(CACHE_VERSION_PREFIX, image_id), version, TIMEOUT)
		image_memcache_key = "%s_%s_%s_%i_%i" %(IMAGE_PREFIX, image_id, version, -1, -1)
		cache.set(image_memcache_key, image_byteString, TIMEOUT)
		return HttpResponse("{'status':'success'}", mimetype='application/json')
		
def getImage(image_id, width, height):
		logging.debug("Getting Image")
		image=Image.objects.get(image_id=image_id)
		logging.debug("Got Image")
		version = image.version
		logging.debug("Image %s" %(version))
		cache.set("%s_%s" %(CACHE_VERSION_PREFIX, image_id), version, TIMEOUT)
		img =image.image_data
		if width!=-1 and height!=-1:
			img = images.Image(image.image_data)
			img.resize(width=width, height=height) 
			img =img.execute_transforms(output_encoding=images.JPEG)
		image_memcache_key = "%s_%s_%s_%i_%i" %(IMAGE_PREFIX, image.image_id, version, width, height)
		logging.debug("Image memcache key: %s" %(image_memcache_key))
		cache.set(image_memcache_key, img, TIMEOUT)
		logging.debug("Returning new image")
		return img
	
