# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('carriera', pkey='id', name_long='!!Carriera', name_plural='!!Carriere', rowcaption='$nome')
        self.sysFields(tbl)
        tbl.column('nome', name_long='!!Nome Carriera')
        tbl.column('ac', 'L', default=0, name_long='!!Ab.Combatt')
        tbl.column('ab', 'L', default=0, name_long='!!Ab.Balistica')
        tbl.column('forza', 'L', default=0, name_long='!!Forza')
        tbl.column('resistenza', 'L', default=0, name_long='!!Resistenza')
        tbl.column('agilita', 'L', default=0, name_long='!!Agilità')
        tbl.column('intelligenza', 'L', default=0, name_long='!!Intelligenza')
        tbl.column('volonta', 'L', default=0, name_long='!!Volonta')
        tbl.column('simpatia', 'L', default=0, name_long='!!Simpatia')
        tbl.column('attacchi', 'L', default=0, name_long='!!Attacchi')
        tbl.column('ferite', 'L', default=0, name_long='!!Ferite')
        tbl.column('bonus_forza', 'L', default=0, name_long='!!Bonus Forza')
        tbl.column('bonus_res', 'L', default=0, name_long='!!Bonus Resistenza')
        tbl.column('mov', 'L', default=0, name_long='!!Movimento')
        tbl.column('magia', 'L', default=0, name_long='!!Magia')
        tbl.column('follia', 'L', default=0, name_long='!!Punti Follia')
        tbl.column('fato', 'L', default=0, name_long='!!Punti Fato')