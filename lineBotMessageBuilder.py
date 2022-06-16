from linebot.models import (
    TemplateSendMessage,
    MessageTemplateAction,
    ButtonsTemplate,
    URITemplateAction,
    CarouselTemplate,
    CarouselColumn,
    TextSendMessage
)

class LineBotMessageBuilder():
  message = None
  template = None
  carouselColumn = None
  carouselColumns = []
  actions = []

  def start_building_template_message(self, alt_text: str = "電腦不支援此訊息格式"):
    self.reset()
    self.message = TemplateSendMessage(
      alt_text = alt_text
    )

  def add_button_template(self, title: str = None, text: str = None, thumbnail_image_url: str = None):
    self.template = ButtonsTemplate(
      title = title,
      text = text,
      thumbnail_image_url = thumbnail_image_url
    )

  def start_building_carousel_template(self):
    self.template = CarouselTemplate()
    self.carouselColumns = []
    self.actions = []
  
  def add_template(self, template):
    self.template = template

  def add_message_template_action(self, label: str = None, text: str = None):
    self.actions.append(MessageTemplateAction(label, text))

  def add_uri_template_action(self, label: str = None, uri: str = None, alt_uri: str = None):
    self.actions.append(URITemplateAction(label, uri, alt_uri))

  def add_carousel_column(self, title: str = None, text: str = None, thumbnail_image_url: str = None):
    if self.carouselColumn is not None:
      self.carouselColumn.actions = self.actions
      self.carouselColumns.append(self.carouselColumn)
      self.actions = []

    self.carouselColumn = CarouselColumn(
        title = title,
        text = text,
        thumbnail_image_url = thumbnail_image_url,
    )
  
  def end_building_carousel_template(self):
    if self.carouselColumn is not None:
      self.carouselColumn.actions = self.actions
      self.carouselColumns.append(self.carouselColumn)
      self.carouselColumn = None
      self.actions = []

  def build(self):
    if len(self.carouselColumns) > 0:
      self.template.columns = self.carouselColumns
    else:
      self.template.actions = self.actions
    self.message.template = self.template
    return self.message

  def buildTextSendMessage(self, text: str = None):
    return TextSendMessage(text)

  def reset(self):
    self.message = None
    self.template = None
    self.carouselColumn = None
    self.carouselColumns = []
    self.actions = []
