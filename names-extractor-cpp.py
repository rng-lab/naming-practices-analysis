
import subprocess
import re
import mysql.connector
import os
import time

from sys import stdout
from bs4 import BeautifulSoup as bs

database = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456789",
    database="NAMING_CATEGORIES"
)

mycursor = database.cursor()

# arq = input('arquivo:\n')

arq = []


def catchLanguage(unitName):

    if 'language="C++"' in unitName:
        return True
    return False


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
        # print(a)
        if(re.search("<name><name>Map</name>", a) == None):
            # print(a)
            a2 = re.sub('<range>.+|<init>.+|<expr>.+', '', a)

            stringFor = re.findall(
                ' <name>\w+</name> |<type><name>\w+</name></type>|<name>\w+</name></type>|<type>.+\w+</name>|<type ref="prev"/><name>\w+</name>| <name>\w+</name><r| <name>\w+</name><init>', a)

            if(re.search('<index>', a)):
                # print("---------",(str(re.findall('\w+</name><index>.+</type>',a))))
                if(re.findall('\w+</name><index>.+</type>', a)):
                    x = re.findall('<decl>.+\w+</name><index>.+</type>', a)
                    # print("INDEXXXXXXXXXXXXXXXXX")
                    if(len(x) > 0):
                        # print("aqui",x[0])

                        tipo = sub(x[0])
                        # print(tipo)
                        identificador = (re.findall(
                            ' <name>\w+</name> | <name>\w+</name><r| <name>\w+</name><i| <name>\w+</name><p| <name>\w+</name></d| <name>\w+</name><[a-z]+', a))
                        codTipo = True
                        if(len(identificador) > 0):
                            identificador = re.sub(
                                '<name>|</name>|<r|<i|<p|</d|<[a-z]+', '', identificador[0])
                            # print("ID: ",identificador)
                            codId = True

                elif(re.findall(' <name>.+\w+</name><index>', a2)):

                    # print(a)

                    certo = re.findall('\w+</name><index>', a)
                    # certo = sub(certo)
                    # print("INDEX22222222")

                    if(len(certo) > 0):
                        certo = sub(certo[0])
                        stringFor.append(certo)

            for tipoId in stringFor:
                # print("tipoID: ",tipoId, type(tipoId))

                match = sub(tipoId)

                if(re.search('</type>|<type>', tipoId)):
                    # print(tipoId)
                    if(re.search('\w+</name><index>.*</type>', a2) == None):
                        # print("----------------------------------------------------------------------------------------------------------",tipoId)
                        tipo = re.findall('\w+</name>.*</type>', tipoId)

                        # tipo = re.sub(' <name>\w+<name> ',"",tipo)
                        # print("começa ",tipo,' END')
                        if(len(tipo) > 0):
                            tipo = sub(tipo[0])
                            # print("Tipo:",tipo)
                            codTipo = True
                            # tava a antes
                        identificador = (re.findall(
                            ' <name>\w+</name> | <name>\w+</name><r| <name>\w+</name><i| <name>\w+</name><p| <name>\w+</name></d| <name>\w+</name><[a-z]+', a))

                        if(len(identificador) > 0):
                            identificador = re.sub(
                                '<name>|</name>|<r|<i|<p|</d|<[a-z]+', '', identificador[0])
                            # print("ID: ",identificador)
                            codId = True

                elif(re.search('<type ref="prev"/>', tipoId)):
                    # print(tipoId)
                    # print("ref tipo: id",match)
                    identificador = match
                    # codTipo = True
                    codId = True

                if(codId == True and codTipo == True):
                    # print(" ADICIONADO tipo: ", tipo, "id: ",
                    #       identificador, "classe: ", classe)
                    # print(a)
                    try:
                        mycursor.execute('INSERT INTO Identificador (nome,tipo,posicao,projeto,arquivo, nomeClasse, nomeMetodo) VALUES("{}","{}","{}","{}","{}","{}","{}")'.format(
                            identificador, tipo, posicao, arq, arquivoAtual, classe, metodo))
                        database.commit()
                    except:
                        pass
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

    # print(identificadoresGeraisComClasse)
    # identificadoresGeraisComClasse[0] = re.sub('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',"",identificadoresGeraisComClasse[0])
    # print(re.match('</name>',identificadoresGeraisComClasse[0]) , "--",arq)
    # identificadoresGeraisComClasse = identificadoresGeraisComClasse.decode('utf-8').split("\n")

    for i in range(tamanhoString):
        # print("---------------")
        # print(identificadoresGeraisComClasse[i])
        # print("---------------FIM DA CLASSE")
        #     ids = str(ids)
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

        # print(identificadoresGeraisComClasse[i])

        # atributo = subprocess.Popen('srcml --xpath "//src:decl " classeXpath.xml', shell=True,stdout=subprocess.PIPE)
        # atributo = atributo.stdout.read()
        # atributo = atributo.decode('utf-8')
        # print(atributo)
        isCpp = False
        # nome da classe
        nomeClasse = subprocess.Popen('srcml --xpath "//src:class/src:name" classeXpath.xml',
                                      shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nomeClasse = nomeClasse.stdout.read()
        nomeClasse = nomeClasse.decode('utf-8')
        if(nomeClasse != '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0"/>\n'):

            nomeClasseUse = catchClassName(nomeClasse)
            isCpp = catchLanguage(nomeClasse)

        nomeClasse = subprocess.Popen('srcml --xpath "//src:class/src:super/src:name" classeXpath.xml',
                                      shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nomeClasse = nomeClasse.stdout.read()
        nomeClasse = nomeClasse.decode('utf-8')
        if(nomeClasse != '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0"/>\n'):
            nomeClasseUse = catchClassName(nomeClasse)
            isCpp = catchLanguage(nomeClasse)

        nomeClasse = subprocess.Popen('srcml --xpath "//src:class/src:annotation/src:name" classeXpath.xml',
                                      shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nomeClasse = nomeClasse.stdout.read()
        nomeClasse = nomeClasse.decode('utf-8')
        if(nomeClasse != '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0"/>\n'):
            nomeClasseUse = catchClassName(nomeClasse)
            isCpp = catchLanguage(nomeClasse)

        # print(nomeClasseUse)

        # todos ids atributos
        identificadoresAtributo = subprocess.Popen(
            'srcml --xpath "//src:decl[not(ancestor::src:for) and not(ancestor::src:while) and not(ancestor::src:do) and not(ancestor::src:if_stmt) and not(ancestor::src:switch) and not(ancestor::src:case) and not(ancestor::src:function) and not(ancestor::src:parameter_list)] " classeXpath.xml', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        identificadoresAtributo = identificadoresAtributo.stdout.read()
        if(isCpp):
            identificadoresAtributo = identificadoresAtributo.decode(
                'utf-8').split("</unit>")
            catchTypeId(identificadoresAtributo, "Atributo",
                        arq, nomeClasseUse, nomefunc)
            # for ids in identificadoresAtributo:
            #     print(ids)

        identificadoresGeraisFuncao = subprocess.Popen(
            'srcml --xpath "//src:function " classeXpath.xml', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        identificadoresGeraisFuncao = identificadoresGeraisFuncao.stdout.read()
        identificadoresGeraisFuncao = identificadoresGeraisFuncao.decode(
            'utf-8')
        identificadoresGeraisFuncao = identificadoresGeraisFuncao.split(
            "</unit>")
        tamanhoFunc = len(identificadoresGeraisFuncao)
        # for func in identificadoresGeraisFuncao:
        #     print(func)
        #     print("--------")
        for j in range(tamanhoFunc):

            # print(identificadoresGeraisFuncao[j])
            fileFunc = open("funcXpath.xml", "w")

            if(j != 0):

                fileFunc.write(
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
                fileFunc.write(
                    '\n<unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0" url=".">')
            # print(identificadoresGeraisFuncao[j])

            identificadoresGeraisFuncao[j] = re.sub(
                'item="\d*"| item="\d* " ', " ", identificadoresGeraisFuncao[j])
            # identificadoresGeraisFuncao[j] = re.sub('item="\d*">', ">",identificadoresGeraisFuncao[j])

            fileFunc.write(identificadoresGeraisFuncao[j])
            fileFunc.write("\n</unit></unit>")
            fileFunc.close()
            # print(identificadoresGeraisFuncao[j])

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

            # for id in idVariavel:
            #     print(id)
            if(isCpp):
                catchTypeId(idVariavel, "Variavel", arq,
                            nomeClasseUse, nomefunc)

        nomefunc = None

        # # função
        # identificadoresVariável = subprocess.Popen('srcml --xpath "//src:decl_stmt[ancestor::src:function[1]]" classeXpath.xml', shell=True,stdout=subprocess.PIPE)
        # identificadoresVariável = identificadoresVariável.stdout.read()
        # identificadoresVariável = identificadoresVariável.decode('utf-8').split("\n")
        # # for ids in identificadoresVariável:
        #     print(ids)
        # catchTypeId(identificadoresVariável,"Variavel",arq)

        identificadorFor = subprocess.Popen(
            'srcml --xpath "//src:decl_stmt[ancestor::src:for[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorFor = identificadorFor.stdout.read()
        identificadorFor = identificadorFor.decode('utf-8').split("\n")
        # for ids in identificadorFor:
        #     print(ids)
        if(isCpp):
            catchTypeId(identificadorFor, "For", arq, nomeClasseUse, nomefunc)

        identificadorWhile = subprocess.Popen(
            'srcml --xpath "//src:decl[ancestor::src:while[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorWhile = identificadorWhile.stdout.read()
        identificadorWhile = identificadorWhile.decode('utf-8').split("\n")
        if(isCpp):
            catchTypeId(identificadorWhile, "while",
                        arq, nomeClasseUse, nomefunc)
        # for id in identificadorWhile:
        #     print(id)

        # do
        identificadorDo = subprocess.Popen(
            'srcml --xpath "//src:decl[ancestor::src:do[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorDo = identificadorDo.stdout.read()
        identificadorDo = identificadorDo.decode('utf-8').split("\n")
        if(isCpp):
            catchTypeId(identificadorDo, "Do", arq, nomeClasseUse, nomefunc)
        # for id in identificadorDo:
        #     print(id)

        # switch
        identificadorswitch = subprocess.Popen(
            'srcml --xpath "//src:decl[ancestor::src:switch[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorswitch = identificadorswitch.stdout.read()
        identificadorswitch = identificadorswitch.decode('utf-8').split("\n")
        if(isCpp):
            catchTypeId(identificadorswitch, "switch",
                        arq, nomeClasseUse, nomefunc)
        # for id in identificadorswitch:
        #     print(id)

        # case
        identificadorCase = subprocess.Popen(
            'srcml --xpath "//src:decl[ancestor::src:case[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorCase = identificadorCase.stdout.read()
        identificadorCase = identificadorCase.decode('utf-8').split("\n")
        if(isCpp):
            catchTypeId(identificadorCase, "Case",
                        arq, nomeClasseUse, nomefunc)
        # for id in identificadorCase:
        #     print(id)

        # if
        identificadorIf = subprocess.Popen(
            'srcml --xpath "//src:decl[ancestor::src:if_stmt[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorIf = identificadorIf.stdout.read()
        identificadorIf = identificadorIf.decode('utf-8').split("\n")
        # for ids in identificadorIf:
        #     print(ids)
        if(isCpp):
            catchTypeId(identificadorIf, "if", arq, nomeClasseUse, nomefunc)

        identificadorParameter = subprocess.Popen(
            'srcml --xpath "//src:decl[ancestor::src:parameter_list[1]]" classeXpath.xml', shell=True, stdout=subprocess.PIPE)
        identificadorParameter = identificadorParameter.stdout.read()
        identificadorParameter = identificadorParameter.decode('utf-8').split("\n")
        # for ids in identificadorParameter:
        #     print(ids)
        if(isCpp):
            catchTypeId(identificadorParameter, "Parameter", arq, nomeClasseUse, nomefunc)

    # identificadorIf = subprocess.Popen('srcml --xpath "//src:decl/ancestor::src:if_stmt[1][not(ancestor::src:while[1])] " classeXpath.xml', shell=True,stdout=subprocess.PIPE)
    # identificadorIf = identificadorIf.stdout.read()
    # identificadorIf = identificadorIf.decode('utf-8').split("\n")
    # # for ids in identificadorIf:
    # #     print(ids)

    # pegar ids declarados na condição do for
    # arquivos = subprocess.Popen('srcml --xpath "//src:for/src:control/src:init/src:decl" classeXpath.xml.xml', shell=True,stdout=subprocess.PIPE)
    # arquivos = arquivos.stdout.read()
    # arquivos = arquivos.decode('utf-8').split("\n")
    # for ids in arquivos:
    #     print(ids)


def main():

    arq = os.listdir()
    # print(arq)
    for arquivo in arq:

        if(re.search(".xml", arquivo) and arquivo != "classeXpath.xml" and arquivo != "funcXpath.xml"):
            run(arquivo)
            # print(arquivo)


if __name__ == '__main__':

    main()
