
import subprocess
import re
import mysql.connector
import os
from sys import stdout
from lxml import etree as et
import libxml2
from bs4 import BeautifulSoup as bs
import time

database = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)

mycursor = database.cursor()


arq = []


def catchPath(unitName):

    pathName = (re.findall('filename="\w+./.*', unitName))
    if(len(pathName) > 0):
        return pathName[0]
    return ''


def sub(tipoId):
    return re.sub('<name>+|</name>|</type>|<type>|<type ref="prev"/>|<index>\[]</index>|<index>|</index>|<decl>|<specifier>.+</specifier>|<range>|<init>|<.+>|<|>|:', "", tipoId)


def catchClassName(unitName):

    nameBracket = (re.findall("<name>\w*</name>", unitName))
    name = re.sub('<name>|</name>', '', nameBracket[0])
    return name


def catchTypeId(arquivos, posicao, arq, classe, metodo):
    codTipo = None
    codId = None
    arquivoAtual = None
    for a in arquivos:
      
        if(re.search("<name><name>Map</name>", a) == None):
           
            a2 = re.sub('<range>.+|<init>.+|<expr>.+', '', a)

            stringFor = re.findall(
                ' <name>\w+</name> |<type><name>\w+</name></type>|<name>\w+</name></type>|<type>.+\w+</name>|<type ref="prev"/><name>\w+</name>| <name>\w+</name><r| <name>\w+</name><init>', a)

            if(re.search('<index>', a)):
            
                if(re.findall('\w+</name><index>.+</type>', a)):
                    x = re.findall('<decl>.+\w+</name><index>.+</type>', a)
                   
                    if(len(x) > 0):
                   

                        tipo = sub(x[0])
                  
                        identificador = (re.findall(
                            ' <name>\w+</name> | <name>\w+</name><r| <name>\w+</name><i| <name>\w+</name><p| <name>\w+</name></d| <name>\w+</name><[a-z]+', a))
                        codTipo = True
                        if(len(identificador) > 0):
                            identificador = re.sub(
                                '<name>|</name>|<r|<i|<p|</d|<[a-z]+', '', identificador[0])
                      
                            codId = True

                elif(re.findall(' <name>.+\w+</name><index>', a2)):

         

                    certo = re.findall('\w+</name><index>', a)
                

                    if(len(certo) > 0):
                        certo = sub(certo[0])
                        stringFor.append(certo)

            for tipoId in stringFor:
          

                match = sub(tipoId)

                if(re.search('</type>|<type>', tipoId)):
               
                    if(re.search('\w+</name><index>.*</type>', a2) == None):
             
                        tipo = re.findall('\w+</name>.*</type>', tipoId)

                        if(len(tipo) > 0):
                            tipo = sub(tipo[0])
                   
                            codTipo = True
                    
                        identificador = (re.findall(
                            ' <name>\w+</name> | <name>\w+</name><r| <name>\w+</name><i| <name>\w+</name><p| <name>\w+</name></d| <name>\w+</name><[a-z]+', a))

                        if(len(identificador) > 0):
                            identificador = re.sub(
                                '<name>|</name>|<r|<i|<p|</d|<[a-z]+', '', identificador[0])
                    
                            codId = True

                elif(re.search('<type ref="prev"/>', tipoId)):
        
                    identificador = match
          
                    codId = True

                if(codId == True and codTipo == True):
          
                    mycursor.execute('INSERT INTO Identificador (nome,tipo,posicao,projeto,arquivo, nomeClasse, nomeMetodo) VALUES("{}","{}","{}","{}","{}","{}","{}")'.format(
                        identificador, tipo, posicao, arq, arquivoAtual, classe, metodo))
                    database.commit()
                    codId = False
                    codTipo = False


def run(arq):

    identificadoresGeraisComClasse = subprocess.Popen('srcml --xpath "//src:class " {}'.format(
        arq), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    identificadoresGeraisComClasse = identificadoresGeraisComClasse.stdout.read()
    identificadoresGeraisComClasse = identificadoresGeraisComClasse.decode(
        'utf-8')
    identificadoresGeraisComClasse = identificadoresGeraisComClasse.split(
        "</unit>")
    tamanhoString = len(identificadoresGeraisComClasse)


    for i in range(tamanhoString):
    
        fileId = open("classeXpath.xml", "w")
        if(i != 0):

            fileId.write(
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
            fileId.write(
                '\n<unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0" url=".">')

        identificadoresGeraisComClasse[i] = re.sub(
            'item="\d*"| item="\d* " ', " ", identificadoresGeraisComClasse[i])
        fileId.write(identificadoresGeraisComClasse[i])
        fileId.write("\n</unit></unit>")
        fileId.close()
        nomefunc = None


        # nome da classe
        nomeClasse = subprocess.Popen('srcml --xpath "//src:class/src:name" classeXpath.xml',
                                      shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nomeClasse = nomeClasse.stdout.read()
        nomeClasse = nomeClasse.decode('utf-8')
        if(nomeClasse != '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0"/>\n'):

            nomeClasseUse = catchClassName(nomeClasse)
            nomePath = catchPath(nomeClasse)
      
      

        nomeClasse = subprocess.Popen('srcml --xpath "//src:class/src:super/src:name" classeXpath.xml',
                                      shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nomeClasse = nomeClasse.stdout.read()
        nomeClasse = nomeClasse.decode('utf-8')
        if(nomeClasse != '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0"/>\n'):
            nomeClasseUse = catchClassName(nomeClasse)
       

        nomeClasse = subprocess.Popen('srcml --xpath "//src:class/src:annotation/src:name" classeXpath.xml',
                                      shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nomeClasse = nomeClasse.stdout.read()
        nomeClasse = nomeClasse.decode('utf-8')
        if(nomeClasse != '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0"/>\n'):
            nomeClasseUse = catchClassName(nomeClasse)

 

        # todos ids atributos
        identificadoresAtributo = subprocess.Popen(
            'srcml --xpath "//src:decl[not(ancestor::src:for) and not(ancestor::src:while) and not(ancestor::src:do) and not(ancestor::src:if_stmt) and not(ancestor::src:switch) and not(ancestor::src:case) and not(ancestor::src:function) and not(ancestor::src:parameter_list)] " classeXpath.xml', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        identificadoresAtributo = identificadoresAtributo.stdout.read()
        identificadoresAtributo = identificadoresAtributo.decode(
            'utf-8').split("</unit>")
        catchTypeId(identificadoresAtributo, "Atributo",
                    arq, nomeClasseUse, nomefunc)
  

        identificadoresGeraisFuncao = subprocess.Popen(
            'srcml --xpath "//src:function " classeXpath.xml', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        identificadoresGeraisFuncao = identificadoresGeraisFuncao.stdout.read()
        identificadoresGeraisFuncao = identificadoresGeraisFuncao.decode(
            'utf-8')
        identificadoresGeraisFuncao = identificadoresGeraisFuncao.split(
            "</unit>")
        tamanhoFunc = len(identificadoresGeraisFuncao)

        for j in range(tamanhoFunc):

        
            fileFunc = open("funcXpath.xml", "w")

            if(j != 0):

                fileFunc.write(
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
                fileFunc.write(
                    '\n<unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0" url=".">')
         

            identificadoresGeraisFuncao[j] = re.sub(
                'item="\d*"| item="\d* " ', " ", identificadoresGeraisFuncao[j])
        

            fileFunc.write(identificadoresGeraisFuncao[j])
            fileFunc.write("\n</unit></unit>")
            fileFunc.close()
    

            # nome da funcao
            nomefunc = subprocess.Popen(
                'srcml --xpath "string(//src:function/src:name) " funcXpath.xml', shell=True, stdout=subprocess.PIPE)
            nomefunc = nomefunc.stdout.read()
            nomefunc = nomefunc.decode('utf-8')

            # variaveis dentro de uma funcao
            idVariavel = subprocess.Popen(
                'srcml --xpath "//src:decl_stmt[ancestor::src:function[1]] " funcXpath.xml', shell=True, stdout=subprocess.PIPE)
            idVariavel = idVariavel.stdout.read()
            idVariavel = idVariavel.decode('utf-8').split("</unit>")

       

            catchTypeId(idVariavel, "Variavel", arq, nomeClasseUse, nomefunc)

        nomefunc = None

       

        identificadorFor = subprocess.Popen(
            'srcml --xpath "//src:decl_stmt[ancestor::src:for[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorFor = identificadorFor.stdout.read()
        identificadorFor = identificadorFor.decode('utf-8').split("\n")
   
        catchTypeId(identificadorFor, "For", arq, nomeClasseUse, nomefunc)

        identificadorWhile = subprocess.Popen(
            'srcml --xpath "//src:decl[ancestor::src:while[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorWhile = identificadorWhile.stdout.read()
        identificadorWhile = identificadorWhile.decode('utf-8').split("\n")
        catchTypeId(identificadorWhile, "while", arq, nomeClasseUse, nomefunc)
     

        # do
        identificadorDo = subprocess.Popen(
            'srcml --xpath "//src:decl[ancestor::src:do[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorDo = identificadorDo.stdout.read()
        identificadorDo = identificadorDo.decode('utf-8').split("\n")
        catchTypeId(identificadorDo, "Do", arq, nomeClasseUse, nomefunc)
   

        # switch
        identificadorswitch = subprocess.Popen(
            'srcml --xpath "//src:decl[ancestor::src:switch[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorswitch = identificadorswitch.stdout.read()
        identificadorswitch = identificadorswitch.decode('utf-8').split("\n")
        catchTypeId(identificadorswitch, "switch",
                    arq, nomeClasseUse, nomefunc)


        # case
        identificadorCase = subprocess.Popen(
            'srcml --xpath "//src:decl[ancestor::src:case[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorCase = identificadorCase.stdout.read()
        identificadorCase = identificadorCase.decode('utf-8').split("\n")
        catchTypeId(identificadorCase, "Case", arq, nomeClasseUse, nomefunc)
   

        # if
        identificadorIf = subprocess.Popen(
            'srcml --xpath "//src:decl[ancestor::src:if_stmt[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorIf = identificadorIf.stdout.read()
        identificadorIf = identificadorIf.decode('utf-8').split("\n")
    
        catchTypeId(identificadorIf, "if", arq, nomeClasseUse, nomefunc)


def main():

    arq = os.listdir()
    # print(arq)
    for arquivo in arq:

        if(re.search(".xml", arquivo) and arquivo != "classeXpath.xml" and arquivo != "funcXpath.xml"):
            # run(arquivo)
            print(arquivo)


if __name__ == '__main__':

    main()
