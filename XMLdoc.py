import datetime
import xml.dom.minidom
from xml.dom import minidom
from chardet.universaldetector import UniversalDetector
import xml.etree.ElementTree as ET
import io
import os
import re
class XMLdoc:
    def __init__(self,upload_folder, output_dir,output_file, OrgStatus, EgrulNotIncluded, svr_version):
        # self.Xml_doc=_Xml_doc
        self.upload_folder = upload_folder
        self.output_dir = output_dir
        self.output_file = output_file
        self.full_path= os.path.join(upload_folder,output_dir,output_file)
        self.OrgStatus = OrgStatus
        self.EgrulNotIncluded = EgrulNotIncluded
        self.svr_version = svr_version
        self.convert_encoding(self.check_encoding()['encoding'],"utf-8")
        self.doc = self.parse_xml(self.full_path)

    @staticmethod
    def open_file(file, encoding ="utf-8"):
        array = []
        with io.open(file,"r",encoding=encoding) as fr:
            array = fr.readlines()
            fr.close()
        return array

    @staticmethod
    def write_file(array,file,encoding="utf-8"):
        with io.open(file, "w", encoding=encoding) as fw:
            fw.writelines(array)
            fw.close()

    def backup_file(self,old,new,encoding="utf-8"):
        arr = self.open_file(old, encoding)
        self.write_file(arr,new,encoding)

    def convert_encoding(self,old_encoding, new_encoding):
        temp_var = old_encoding
        arr = self.open_file(self.full_path, old_encoding)
        self.write_file(arr,self.full_path,new_encoding)

    def check_encoding(self):
        detector = UniversalDetector()
        with open(self.full_path, 'rb') as fh:
            for line in fh:
                detector.feed(line)
                if detector.done:
                    break
            detector.close()
        return detector.result


# В отличии от set, актуализирует связку upload_folder+ output_folder+ output_file
    def update_full_path(self):
        self.full_path=self.upload_folder+'//'+self.output_dir+'//'+self.output_file
    def set_output_file(self, output_file):
        self.output_file=output_file
    # def restore_subs(self,arr,main_arr):
    #     for elem in main_arr[i]:
    #         if len(elem):
    #             ET.SubElement()

    def rec_edit(self,element,parent, search_attr='name', search_attr_value='value', change_attrib='text', change_attrib_value='text'):
        if parent.find(element.tag) == None:
            for i in range(len(parent)):
                if len(parent[i]): # если что-то вложено ещё
                    self.rec_edit(element,parent[i],search_attr,search_attr_value,change_attrib,change_attrib_value)
        else:
            #Наверное лучше настроить поиск не по аттрибутам элементов, а по соотношению родитель/элемент
            if element.get(search_attr) == search_attr_value:
                element.set(change_attrib,change_attrib_value)

    def rec_remove(self,element,parent):
        if parent.find(element.tag) == None:
            for i in range(len(parent)):
                if len(parent[i]): # если что-то вложено ещё
                    self.rec_remove(element,parent[i])
        else:
            #
            #try:
            elem=parent.find(element.tag)
            #l = list(parent)
            parent.remove(elem)
            #except (ValueError):
            #    pass
        # result=[]
        # src_arr = arr
        # for i in range(len(arr)):
        #     if len(arr[i]):
        #         #d = list(arr[i].iter())
        #         for sub in arr[i]:
        #             arr[i].remove(sub)
        # full = self.restore_subs(arr[i],arr)
        # self.restore_subs(arr[i], arr)
        # b = arr[i]
        # a = ET.tostring(arr[i], encoding='utf-8').decode("utf-8")
        # result.append(a)

        #return ''.join(result)

    #преобразуем xml в ET и назначим рабочее пространство в row
    @staticmethod
    def parse_xml(file,encoding="utf-8"):
        parser = ET.XMLParser(encoding=encoding)
        doc = ET.parse(file, parser)
        return doc

    def del_elem(self,elem, parent):
        element= parent.iter(elem)
        if parent.find(elem.tag) != None:
            parent.remove(elem)
        else:
            for child in parent:
                res = list(child.iterfind(elem.tag))
                if res != []:
                    self.del_elem(elem,child)

    def status_change(self,element, status):
        if element.tag == "RecordNum":
            element.text = element.text[:-1] + status
        elif element.tag == "OrgStatus":
            element.text = status
    def Egrul_status_change(self, element, bools):
        if element.tag == "EGRULNotIncluded":
            element.text = bools
    # Status изменим


    def remove_header(self,encoding="utf-8"):
        row_root = self.doc.getroot()
        for child in row_root.iter():
            row = child.find('row')
            if row != None:
                break

        #rows = root.iterfind('row')
        self.doc = ET.ElementTree(row)
        #root = newdoc.getroot()
        #newdoc.write(self.full_path,encoding=encoding)

    #Другие названния нужны для отладки. Похже сменю на основные
    def edit_xml(self,encoding="utf-8"):

        root = self.doc.getroot()
        root.set("xmlns","")

        for child in enumerate(root.iter()):
            # Обязательная настройка
            if child[1].tag == "StartDateActive" and root.find("NoInternet")==None:
                new=ET.Element("NoInternet", {})
                new.text="false"
                root.insert(child[0], new )
            elif child[1].tag == "OrgCode":
                self.set_output_file(child[1].text+'.xml')
            elif child[1].tag == "IsObosob" and child[1].text == "1":
                print("проверьте, что правильный статус указан у головной организации")
            # elif child[1].tag == "IsConfidantUCFK":
            #     self.rec_remove(child[1], root)
            # elif 'OgrDos' in child[1].tag:
            #     self.rec_remove(child[1], root)
            self.Egrul_status_change(child[1], self.EgrulNotIncluded)
            self.status_change(child[1], self.OrgStatus)
            print(child[1])

        ref_root = ET.Element('REF_UBPandNUBP', attrib={'version': '2.1', 'xmlns': "http://www.roskazna.ru/eb/domain/REF_UBPandNUBP/formular"})
        for child in enumerate(ref_root.iter()):
            if 'REF_UBPandNUBP' in child[1].tag:
                child[1].append(root)
                if child[1].get('version') == '2.1':
                    child[1].set('version', self.svr_version)
                #self.rec_edit(child[1], ref_root, search_attr='version', search_attr_value='2.1',change_attrib='version', change_attrib_value=self.svr_version) # если parent и element совпадают
        #ET.SubElement(ref_root, root)
        self.doc = ET.ElementTree(ref_root)
        self.doc.write(self.full_path, encoding=encoding)

    #Разбивка идёт по закрывающему тэгу
    def set_header(self,header, encoding="utf-8", INC="", environment="PROD", splitter = "</typ:document>", template='ul_template.xml'):
        #Записываем временный заголовок
        template_tmp = 'tmp_'+header
        #ET.register_namespace('xmlns',"http://www.roskazna.ru/eb/domain/REF_UBPandNUBP/formular")
        ET.register_namespace('soapenv',"http://schemas.xmlsoap.org/soap/envelope/")
        ET.register_namespace('typ',"http://www.roskazna.ru/eb/services/transferDocumentService/types")
        #xmlns = "http://www.roskazna.ru/eb/domain/REF_UBPandNUBP/formular"
        root_template = self.parse_xml(header)
        root_template = root_template.getroot()
        for child in enumerate(root_template.iter()):
            print(child)
        root = self.doc.getroot()

        #Заменяем
        for child in enumerate(root_template.iter()):
            if 'param' in child[1].tag:
                if child[1].get('name') == 'versionId':
                    child[1].set('value', self.svr_version)
                #self.rec_edit(child[1],root_template, search_attr='name',search_attr_value='versionId',change_attrib='value', change_attrib_value=self.svr_version)
                    break

        for child in enumerate(root_template.iter()):
            if re.fullmatch(r'.*document\d{0}', child[1].tag):
                child[1].append(root)
                break

        #result = ET.tostring(root_template,encoding='unicode').split('\n')
        result = ET.ElementTree(root_template)
        #self.write_file(result,self.full_path)
        #print(enumerate(root_template.iter()))
        result.write(self.full_path, encoding=encoding)

        # # # ПРОШЛАЯ РЕАЛИЗАЦИЯ
        # root_template = ET.ElementTree(root_template)
        # root_template.write(template_tmp,encoding=encoding)
        # arr_src = self.open_file(file=self.full_path)
        # arr_header = self.open_file(file=template)
        # arr_header = self.open_file(file=header)
        # for item in enumerate(arr_header):
        #     if splitter in item[1]:
        #         result=arr_header[:item[0]]+arr_src+arr_header[item[0]:]
        #         #Можно сначала сделать
        #         self.update_full_path()
        #         self.write_file(result, self.full_path)
        #         return
                #return self.full_path
                #header=arr_template[item[0]:]
                #close_header=arr[:item[0]]
        # #return ""
    #In-Work
    def canonicalize(self):
        root = self.doc.getroot()
        xml_data = ET.tostring(root)
        #decoded_string = xml_data.decode("UTF-8")
        with open(self.full_path, mode='w', encoding='utf-8') as out_file:
            ET.canonicalize(xml_data , out=out_file)