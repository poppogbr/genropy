#!/usr/bin/env python
# encoding: utf-8
#
# gnrbaghtml.py
#
# Created by Francesco Porcari on 2010-10-16.
# Copyright (c) 2010 Softwell. All rights reserved.

import os
from gnr.core.gnrstring import toText
from gnr.core.gnrhtml import GnrHtmlBuilder
from gnr.core.gnrbag import Bag, BagCbResolver

class BagToHtml(object):
    """add???
    """
    templates = ''
    print_button = None
    rows_path = 'rows'
    encoding = 'utf-8'
    page_debug = False
    page_width = 200
    page_height = 280
    page_margin_top = 0
    page_margin_left = 0
    page_margin_right = 0
    page_margin_bottom = 0
    currencyFormat = u'#,###.00'
    #override these lines
    row_mode = 'value'
    page_header_height = 0 #
    page_footer_height = 0
    page_leftbar_width = 0
    page_rightbar_width = 0
    doc_header_height = 0 # eg 10
    doc_footer_height = 0 # eg 15
    grid_header_height = 0 # eg 6.2
    grid_footer_height = 0
    grid_col_widths = [0, 0, 0]
    grid_row_height = 5
    copies_per_page = 1
    copy_extra_height = 0
    starting_page_number = 0
    css_requires = ''
    
    def __init__(self, locale='en', encoding='utf-8', templates=None, templateLoader=None, **kwargs):
        self.locale = locale
        self.encoding = encoding
        self.thermo_kwargs = None
        self.thermo_wrapper = None
        if templates:
            self.templates = templates
        if templateLoader:
            self.templateLoader = templateLoader
            
    def init(self, *args, **kwargs):
        """add???"""
        pass
        
    def outputDocName(self, ext=''):
        """add???
        
        :param ext: add???. Default value is `` ``
        """
        return 'temp.%s' % ext
        
    def onRecordLoaded(self):
        """override this"""
        pass
        
    def orientation(self):
        """add???
        """
        if self.page_width>self.page_height:
            return 'Landscape'
        else:
            return 'Portrait'
        
    def __call__(self, record=None, filepath=None, folder=None, filename=None, hideTemplate=False, rebuild=True,
                 htmlContent=None, **kwargs):
        """Return the html corresponding to a given record.
        The html can be loaded from a cached document or created if still doesn't exist.
        """
        if record is None:
            record = Bag()
        self.htmlContent = htmlContent
        self._data = Bag()
        self.record = record
        self.setData('record', record) #compatibility
        for k, v in kwargs.items():
            self.setData(k, v)
        if folder and not filepath:
            filepath = os.path.join(folder, filename or self.outputDocName(ext='html'))
        self.filepath = filepath
        
        if not rebuild:
            with open(self.filepath, 'r') as f:
                result = f.read()
            return result
            
        self.templates = kwargs.pop('templates', self.templates)
        self.print_button = kwargs.pop('print_button', self.print_button)
        if self.onRecordLoaded() is False:
            return False
        self.showTemplate(hideTemplate is not True)
        self.htmlTemplate = None
        self.prepareTemplates()
        self.builder = GnrHtmlBuilder(page_width=self.page_width, page_height=self.page_height,
                                      page_margin_top=self.page_margin_top, page_margin_bottom=self.page_margin_bottom,
                                      page_margin_left=self.page_margin_left, page_margin_right=self.page_margin_right,
                                      page_debug=self.page_debug, print_button=self.print_button,
                                      htmlTemplate=self.htmlTemplate, css_requires=self.get_css_requires(),
                                      showTemplateContent=self.showTemplateContent)
        result = self.createHtml(filepath=self.filepath)
        return result

    def get_css_requires(self):
        return self.css_requires.split(',')

    def prepareTemplates(self):
        """add???"""
        if not self.htmlTemplate:
            self.htmlTemplate = self.templateLoader(self.templates)
        self.page_height = self.page_height or self.htmlTemplate['main.page.height'] or 280
        self.page_width = self.page_width or self.htmlTemplate['main.page.width'] or 200
        self.page_header_height = self.page_header_height or  self.htmlTemplate['layout.top?height'] or 0
        self.page_footer_height = self.page_footer_height or  self.htmlTemplate['layout.bottom?height'] or 0
        self.page_leftbar_width = self.page_leftbar_width or  self.htmlTemplate['layout.left?width'] or 0
        self.page_rightbar_width = self.page_leftbar_width or  self.htmlTemplate['layout.right?width'] or 0
        self.page_margin_top = self.page_margin_top or self.htmlTemplate['main.page.top'] or 0
        self.page_margin_left = self.page_margin_left or self.htmlTemplate['main.page.left'] or 0
        self.page_margin_right = self.page_margin_right or self.htmlTemplate['main.page.right'] or 0
        self.page_margin_bottom = self.page_margin_bottom or self.htmlTemplate['main.page.bottom'] or 0
        
    def toText(self, obj, locale=None, format=None, mask=None, encoding=None, **kwargs):
        """add???
        
        :param obj: add???
        :param locale: add???. Default value is ``None``
        :param format: add???. Default value is ``None``
        :param mask: add???. Default value is ``None``
        :param encoding: The multibyte character encoding you choose. Default value is ``None``
        :returns: add???
        """
        locale = locale or self.locale
        encoding = locale or self.encoding
        return toText(obj, locale=locale, format=format, mask=mask, encoding=encoding, **kwargs)
        
    def createHtml(self, filepath=None):
        """add???
        
        :param filepath: add???. Default value is ``None``
        :returns: add???
        """
        #filepath = filepath or self.filepath
        self.initializeBuilder()
        self.main()
        self.builder.toHtml(filepath=filepath)
        return self.builder.html
        
    def showTemplate(self, value):
        """add???
        
        :param value: add???
        :returns: add???
        """
        self.showTemplateContent = value
        
    def setTemplates(self, templates):
        """add???
        
        :param templates: add???
        :returns: add???
        """
        self.templates = templates
        
    def getTemplates(self, templates):
        """add???
        
        :param templates: add???
        :returns: add???
        """
        return self.templates
        
    def initializeBuilder(self):
        """add???"""
        self.builder.initializeSrc()
        self.body = self.builder.body
        self.getNewPage = self.builder.newPage
        self.builder.styleForLayout()
        
    def getData(self, path, default=None):
        """add???
        
        :param path: add???
        :param default: add???. Default value is ``None``
        :returns: add???
        """
        wildchars = []
        if path[0] in wildchars:
            value = 'not yet implemented'
        else:
            value = self._data.getItem(path, default)
        return value
        
    def setData(self, path, value, **kwargs):
        """add???
        
        :param path: add???
        :param value: add???
        """
        self._data.setItem(path, value, **kwargs)
        
    def onRecordExit(self, recordBag):
        """add???
        
        :param recordBag: add???
        """
        return
        
    def field(self, path, default=None, locale=None,
              format=None, mask=None, root=None, **kwargs):
        """add???
        
        :param path: add???
        :param default: add???. Default value is ``None``
        :param locale: add???. Default value is ``None``
        :param format: add???. Default value is ``None``
        :param mask: add???. Default value is ``None``
        :param root: add???. Default value is ``None``
        :returns: add???
        """
        if root is None:
            root = self._data['record']
        attr = {}
        if isinstance(root, Bag):
            datanode = root.getNode(path)
            if datanode:
                value = datanode.value
                attr = datanode.attr
            else:
                value = default
        else:
            value = root.get(path)
        if value is None:
            value = default
        elif isinstance(value, Bag):
            return value
            
        format = format or attr.get('format')
        mask = mask or attr.get('mask')
        return self.toText(value, locale, format, mask, self.encoding, **kwargs)
        
    def main(self):
        """It can be overridden"""
        if self.htmlContent:
            page = self.getNewPage()
            page.div("%s::HTML" % self.htmlContent)
        else:
            self.mainLoop()
            
    def pageCounter(self, mask=None):
        """add???
        
        :param mask: add???. Default value is ``None``
        """
        mask = mask or '%s/%s'
        
        def getPage(currPage=0):
            result = mask % (currPage + 1 + self.starting_page_number,
                             self.copies[self.copy]['currPage'] + 1 + self.starting_page_number)
            return result
            
        return BagCbResolver(getPage, currPage=self.copies[self.copy]['currPage'])
        
    def copyHeight(self):
        """add???"""
        return (self.page_height - self.page_margin_top - self.page_margin_bottom -\
                self.page_header_height - self.page_footer_height -\
                self.copy_extra_height * (self.copies_per_page - 1)) / self.copies_per_page
                
    def copyWidth(self):
        """add???"""
        return (self.page_width - self.page_margin_left - self.page_margin_right -\
                self.page_leftbar_width - self.page_rightbar_width)
                
    def mainLoop(self):
        """add???"""
        self.copies = []
        self.lastPage = False
        self.defineStandardStyles()
        self.defineCustomStyles()
        self.doc_height = self.copyHeight() #- self.page_header_height - self.page_footer_height
        self.grid_height = self.doc_height - self.calcDocHeaderHeight() - self.doc_footer_height
        self.grid_body_height = self.grid_height - self.grid_header_height - self.grid_footer_height
        for copy in range(self.copies_per_page):
            self.copies.append(dict(grid_body_used=self.grid_height, currPage=-1))
            
        lines = self.getData(self.rows_path)
        
        if lines:
            if isinstance(lines, Bag):
                nodes = lines.getNodes()
            elif hasattr(lines, 'next'):
                nodes = list(lines)
                
            if hasattr(self, 'thermo_wrapper') and self.thermo_kwargs:
                nodes = self.thermo_wrapper(nodes, **self.thermo_kwargs)
                
            for rowDataNode in nodes:
                self.currRowDataNode = rowDataNode
                for copy in range(self.copies_per_page):
                    self.copy = copy
                    rowheight = self.calcRowHeight()
                    availableSpace = self.grid_height - self.copyValue('grid_body_used') -\
                                     self.calcGridHeaderHeight() - self.calcGridFooterHeight()
                    if rowheight > availableSpace:
                        self._newPage()
                    row = self.copyValue('body_grid').row(height=rowheight)
                    self.copies[self.copy]['grid_body_used'] = self.copyValue('grid_body_used') + rowheight
                    self.currColumn = 0
                    self.currRow = row
                    self.prepareRow(row)
                    
            for copy in range(self.copies_per_page):
                self.copy = copy
                self._closePage(True)
                
    def _newPage(self):
        if self.copyValue('currPage') >= 0:
            self._closePage()
        self.copies[self.copy]['currPage'] = self.copyValue('currPage') + 1
        self.copies[self.copy]['grid_body_used'] = 0
        self._createPage()
        self._openPage()
        
    def _get_rowData(self):
        if isinstance(self.currRowDataNode, dict):
            return self.currRowDataNode
        elif self.row_mode == 'attribute':
            return self.currRowDataNode.attr
        else:
            return self.currRowDataNode.value
            
    rowData = property(_get_rowData)
    
    def rowField(self, path=None, **kwargs):
        """add???
        
        :param path: add???. Default value is ``None``
        :returns: add???
        """
        #if self.row_mode=='attribute':
        #    data = self.currRowDataNode.attr
        #else:
        #    data = self.currRowDataNode.value
        return self.field(path, root=self.rowData, **kwargs)
        
    def rowCell(self, field=None, value=None, default=None, locale=None,
                format=None, mask=None, currency=None, **kwargs):
        """add???
        
        :param field: add???. Default value is ``None``
        :param value: add???. Default value is ``None``
        :param default: add???. Default value is ``None``
        :param locale: add???. Default value is ``None``
        :param format: add???. Default value is ``None``
        :param mask: add???. Default value is ``None``
        :param currency: add???. Default value is ``None``
        :returns: add???
        """
        if field:
            if callable(field):
                value = field()
            else:
                value = self.rowField(field, default=default, locale=locale, format=format, mask=mask,
                                      currency=currency)
        if value is not None:
            #if self.lastPage:
            #    print 'last page'
            #    print self.currColumn
            #    print self.grid_col_widths[self.currColumn]
            value = self.toText(value, locale, format, mask, self.encoding)
            self.currRow.cell(value, width=self.grid_col_widths[self.currColumn], overflow='hidden',
                              white_space='nowrap', **kwargs)
        self.currColumn = self.currColumn + 1
        return value

    def _createPage(self):
        curr_copy = self.copies[self.copy]
        if self.copy == 0:
            self.paperPage = self.getNewPage()
        self.page_layout = self.mainLayout(self.paperPage)
        #if self.page_header_height:
        #    curr_copy['page_header'] = self.page_layout.row(height=self.page_header_height,lbl_height=4,lbl_class='caption').cell()
        if self.doc_header_height:
            curr_copy['doc_header'] = self.page_layout.row(height=self.calcDocHeaderHeight(), lbl_height=4,
                                                           lbl_class='caption').cell()
        curr_copy['doc_body'] = self.page_layout.row(height=0, lbl_height=4, lbl_class='caption').cell()
        if self.doc_footer_height:
            curr_copy['doc_footer'] = self.page_layout.row(height=self.doc_footer_height, lbl_height=4,
                                                           lbl_class='caption').cell()
            #if self.page_footer_height:
            #    curr_copy['page_footer'] = self.page_layout.row(height=self.page_footer_height,lbl_height=4,lbl_class='caption').cell()
            
    def mainLayout(self, page):
        """must be overridden
        
        :param page: add???
        """
        pass
        
    def _openPage(self):
        #if self.page_header_height:
        #    self.pageHeader(self.copyValue('page_header')) #makeTop
        if self.doc_header_height:
            self.docHeader(self.copyValue('doc_header'))
        self._docBody(self.copyValue('doc_body'))
        
    def _closePage(self, lastPage=None):
        if lastPage:
            self.lastPage = True
        self.fillBodyGrid()
        footer_height = self.calcGridFooterHeight()
        if footer_height:
            row = self.copyValue('body_grid').row(height=footer_height)
            self.currColumn = 0
            self.currRow = row
            self.gridFooter(row)
        if self.doc_footer_height:
            self.docFooter(self.copyValue('doc_footer'), lastPage=lastPage)
            #if self.page_footer_height:
            #    self.pageFooter(self.copyValue('page_footer'),lastPage=lastPage)
            
    def _docBody(self, body):
        header_height = self.calcGridHeaderHeight()
        grid = self.gridLayout(body)
        if header_height:
            self.gridHeader(grid.row(height=header_height))
        self.copies[self.copy]['body_grid'] = grid
        
    def gridLayout(self, grid):
        """It must be overridden
        
        :param grid: add???
        """
        print 'gridLayout must be overridden'
        
    def gridHeader(self, row):
        """It can be overridden
        
        :param row: add???
        """
        lbl_height = 4
        headers = self.grid_col_headers
        if ':' in headers:
            headers, lbl_height = headers.split(':')
            lbl_height = int(lbl_height)
        for k, lbl in enumerate(self.grid_col_headers.split(',')):
            style = None
            if lbl == '|':
                lbl = ''
                style = 'border-top:0mm;border-bottom:0mm;'
            row.cell(lbl=lbl, lbl_height=lbl_height, width=self.grid_col_widths[k], style=style)
            
    def gridFooter(self, row):
        """It can be overridden
        
        :param row: add???
        """
        print 'gridFooter must be overridden'
        
    def fillBodyGrid(self):
        """add???
        """
        row = self.copyValue('body_grid').row()
        for w in self.grid_col_widths:
            row.cell(width=w)
            
    def copyValue(self, valuename):
        """add???
        
        :param valuename: add???
        """
        return self.copies[self.copy][valuename]
        
    def calcRowHeight(self):
        """override for special needs
        
        :returns: add???
        """
        return self.grid_row_height
        
    def calcGridHeaderHeight(self):
        """override for special needs
        
        :returns: add???
        """
        return self.grid_header_height
        
    def calcGridFooterHeight(self):
        """override for special needs
        
        :returns: add???
        """
        return self.grid_footer_height
        
    def calcDocHeaderHeight(self):
        """override for special needs
        
        :returns: add???
        """
        return self.doc_header_height
        
    def defineCustomStyles(self):
        """override this for custom styles
        
        :returns: add???
        """
        pass
        
    def docFooter(self, footer, lastPage=None):
        """add???
        
        :param footer: add???
        :param lastPage: add???. Default value is ``None``
        """
        pass
        
    def pageFooter(self, footer, lastPage=None):
        """add???
        
        :param footer: add???
        :param lastPage: add???. Default value is ``None``
        """
        pass
        
    def pageHeader(self, header):
        """add???
        
        :param header: add???
        """
        pass
        
    def docHeader(self, header):
        """add???
        
        :param header: add???
        """
        pass
        
    def defineStandardStyles(self):
        """add???
        """
        self.body.style("""
                        .caption{text-align:center;
                                 color:gray;
                                 font-size:8pt;
                                 height:4mm;
                                 line-height:4mm;
                                 font-weight: normal;
                                 }
                        .smallCaption{font-size:7pt;
                                  text-align:left;
                                  color:gray;
                                  text-indent:1mm;
                                  width:auto;
                                  font-weight: normal;
                                  line-height:auto;
                                  line-height:3mm;
                                  height:3mm;""")
                                  
        self.body.style("""
                        .extrasmall {font-size:6pt;text-align:left;line-height:3mm;}
                        .textfield {text-indent:0mm;margin:1mm;line-height:3mm}
                        .dotted_bottom {border-bottom:1px dotted gray;}
                                                
                        .aligned_right{
                            text-align:right;
                            margin-right:1mm;
                        }
                        .aligned_left{
                            text-align:left;
                            margin-left:1mm;
                        }
                        .aligned_center{
                            text-align:center;
                        }
                         """)