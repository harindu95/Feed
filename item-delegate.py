from PyQt6.QtGui import QPainter, QPixmap,QFont, QTextDocument, QAbstractTextDocumentLayout, QColor,QRegion
from PyQt6.QtWidgets import QStyle,QStyleOptionViewItem,QStyledItemDelegate
from PyQt6.QtCore import QModelIndex, QSize, QRect, QRectF, Qt


class ItemDelegate(QStyledItemDelegate):

    def get_image_size(self):
        image_width,image_height = 200,160
        return image_width,image_height

    def __init__( self ):
            super().__init__()
            # probably better not to create new QTextDocuments every ms
            self.doc = QTextDocument()

    def process_description(self, txt):
        from bs4 import BeautifulSoup

        plain = ' '.join(BeautifulSoup(txt, "html.parser").findAll(text=True))
        return plain.strip()[:200]
    
    def sizeHint(self, options, index: QModelIndex) -> QSize:
        # options = QtGui.QStyleOptionViewItemV4(option)
        # self.initStyleOption(options,index)
        image_width,image_height = self.get_image_size()
        padding = 20
        item = index.data()
        if item.image_url == '':
            image_width,image_height = 0,0

        width = options.rect.width() - image_width
        self.doc.setTextWidth(width)
        font = QFont(options.font)
        font.setPointSize(14)
        self.doc.setDefaultFont(font)
        self.doc.setHtml(item.title)
        title_height = self.doc.size().height()

        summary = self.process_description(item.summary)
        self.doc.setDefaultFont(options.font)
        self.doc.setHtml(summary)
        summary_height = self.doc.size().height()
        
        size = QSize()
        size.setWidth(options.rect.width())
        h2 = padding + title_height + padding + summary_height
        h = max(image_height + padding + padding , h2 ) 
        # h = max(height, image_height + padding * 2 )
        h = h + 2 #line height
        size.setHeight(h)
        return size

    def paint(self, painter: QPainter, options:QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()
        # options.widget.style().drawControl(QStyle.ControlElement.CE_ItemViewItem, options, painter)
        painter.translate(options.rect.left(), options.rect.top())

        item = index.data()
        x = options.rect.x()
        y = options.rect.y()
        width = options.rect.width()
        height = options.rect.height()
        padding = 20
        painter.translate(0, padding)
        height -= padding
        image_width,image_height = self.get_image_size()

        if item.image_url != '':
            image = item.image_data
            pixmap = QPixmap()
            pixmap.loadFromData(image)
            pixmap = pixmap.scaled(
                image_width, image_height, Qt.AspectRatioMode.KeepAspectRatio,transformMode = Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(QRect(0,0,image_width,image_height) ,pixmap)
            
        else:
            image_width,image_height = 0,0

        width -= padding
        painter.translate(image_width + padding, 0)
        width -= image_width

        self.doc.setHtml(item.title)
        font = QFont(options.font)
        font.setPointSize(14)
        self.doc.setDefaultFont(font)
        clip = QRectF(0, 0, width, height)
        ctx = QAbstractTextDocumentLayout.PaintContext()
        ctx.clip = clip
        self.doc.setTextWidth(width)  
        self.doc.documentLayout().draw(painter, ctx)
        title_height = self.doc.size().height()
        
        painter.translate(0, title_height )
        height = height - title_height

        summary = self.process_description(item.summary)
        self.doc.setHtml(summary)
        font = options.font
        self.doc.setDefaultFont(options.font)
        clip = QRectF(0,0,width, height)
        ctx = QAbstractTextDocumentLayout.PaintContext()
        ctx.clip = clip
        self.doc.documentLayout().draw(painter, ctx)
        summary_height = self.doc.size().height()
        painter.translate(0,summary_height)

        h2 = title_height + summary_height
        if h2 > image_height:
            painter.translate(-image_width -padding, 0)
            painter.fillRect(0,0,options.rect.width(),2, QColor(130,120,130))
        else:
            painter.translate(-image_width -padding, image_height-h2)
            painter.fillRect(0,0,options.rect.width(),2, QColor(130,120,130))
        painter.restore()

