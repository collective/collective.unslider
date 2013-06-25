from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.unslider import MessageFactory as _
from plone.app.portlets.browser import z3cformhelper
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationList, RelationChoice
from collective.sliderfields.interfaces import ISliderFieldsEnabled
from z3c.form import field

class IUnsliderPortlet(IPortletDataProvider):
    """
    Define your portlet schema here
    """
    width = schema.Int(title=_(u'Width'))
    height = schema.Int(title=_(u'Height'))

    contents = RelationList(title=_(u'Contents'),
        value_type=RelationChoice(
            source=ObjPathSourceBinder(object_provides=ISliderFieldsEnabled.__identifier__)
        )
    )

class Assignment(base.Assignment):
    implements(IUnsliderPortlet)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def title(self):
        return _('Unslider Portlet')

class Renderer(base.Renderer):
    
    render = ViewPageTemplateFile('templates/unsliderportlet.pt')

    @property
    def available(self):
        return True

    def contents(self):
        data = []
        for i in self.data.contents:
            obj = self.context.portal_catalog(UID=i.UID())[0].getObject()
            title = getattr(i, 'slider_title', None)
            if not title:
                i.Title()
            description = getattr(i, 'slider_description', None)
            scales = obj.restrictedTraverse('@@images')
            image = scales.scale('slider_image', width=self.data.width,
                                    height=self.data.height)
            data.append({
                'title': title,
                'description': description,
                'image_url': image.url,
                'slide_css': 
                    """
                        height: %spx;
                        width: %spx;
                        background-image:url('%s');
                    """ % (
                        self.data.height, self.data.width, image.url
                    )
            })
        return data


class AddForm(z3cformhelper.AddForm):
    fields = field.Fields(IUnsliderPortlet)
    label = _(u"Add Unslider Portlet")
    description = _(u"")

    def create(self, data):
        return Assignment(**data)

class EditForm(z3cformhelper.EditForm):
    fields = field.Fields(IUnsliderPortlet)
    label = _(u"Edit Unslider Portlet")
    description = _(u"")
