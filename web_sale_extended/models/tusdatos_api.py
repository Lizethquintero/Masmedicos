# -*- coding: utf-8 -*-

import json
import logging
import requests
import time
from requests.auth import HTTPBasicAuth

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# HOW TO CALL API.TUSDATOS

# launch
# # self.env['api.tusdatos'].launch_query_tusdatos(
# #     document: str,
# #     document_type: str,
# #     expedition_date: str = None)

# approval
# # self.env['api.tusdatos'].personal_data_approval(process_id: str)

# specific request to TusDatosAPI
# # self.env['api.tusdatos'].request_tusdatos_api(endpoint: str, query: dict)

class TusDatosAPI(models.TransientModel):
    _name = "api.tusdatos"
    _description = "Api TusDatos"

    def request_tusdatos_api(self, endpoint: str, query: dict) -> dict:
        """El api de tusdatos.co utiliza tecnología REST/JSON, los endpoints se
        refiere a los puntos de comunicaciones establecidos para realizar diferentes
        tipos de acciones sobre nuestra plataforma.
        Para iniciar una consulta se debe realizar una petición post al
        endpoint /api/launch/. Cada petición realizada al api en producción consume
        creditos sobre el plan adquirido. Para conocer el estado de una consulta
        se debe hacer una petición sobre el estado de la tarea en el endpoint
        /api/results/{job-id}. Si la consulta sobre una o más fuentes falla podemos
        reintentar completar la información usando el endpoint /api/retry/{oid}/.

        Este es un ambiente de pruebas que responde de forma estática.
        Credenciales API de prueba son usuario: pruebas, contraseña: password

        Args:
                endpoint: 'http://docs.tusdatos.co/api/{endpoint}'
                    Defualt > 'launch', 'launch/verify', 'launch/car',
                    'retry/{id}', 'results/{job_key}'.
                    Reports > ported 1.0: ['report_pdf/{id}', 'report_nit/{id}',
                    'report_nit_pdf/{id}'], soported: 'report_json/{id'}.
                    User info > 'plans', 'querys'.
                query: params dict.

        Returns:
                Response for api request.

        .. _API REST/JSON documentation:
            http://docs.tusdatos.co/docs

        """
        # TODO: change strings to fields from config module
        username = self.env.user.company_id.mail_tusdatos
        passwrd = self.env.user.company_id.password_tusdatos
        api_post = ['launch', 'launch/verify', 'launch/car']
        api_get = ['retry', 'results', 'report_json', 'plans', 'querys']
        hostname = 'https://dash-board.tusdatos.co/api/'

        if endpoint in api_post:
            headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
            url = f'{hostname}{endpoint}'
            response = requests.post(url, json=query, auth=HTTPBasicAuth(username, passwrd), headers=headers)
        elif endpoint in api_get:
            headers = {'accept': 'application/json'}
            if query.get('jobid'):
                endpoint = f'{endpoint}/{query["jobid"]}'
                url = f'{hostname}{endpoint}'
                response = requests.get(url, auth=HTTPBasicAuth(username, passwrd), headers=headers)
            elif query.get('id'):
                endpoint = f'{endpoint}/{query["id"]}'
                url = f'{hostname}{endpoint}'
                response = requests.get(url, auth=HTTPBasicAuth(username, passwrd), headers=headers)
            else:
                _logger.error(f"****** ERROR: invalid request url: \n{url}\n{query}. ******")
        else:
            raise 'Error: Bad endpoint'

        # TO DO: handler response code != 200
        if response.status_code != 200:
            _logger.error(f'****** ERROR {response.status_code}: validation failled, {response.json()}. ******')
            response.close
            response = response.json()
        else:
            response.close
            response = response.json()
        print(response)
        return response

    def launch_query_tusdatos(self, document: str, document_type: str,
                              expedition_date: str = None) -> dict:
        """

        Args:
            document: número de documento.
            document_type: tipo de documento.
            expedition_date: fecha de expedición.

        Return:
            response dict from tusdatos.co api rest service.
        """
        query, response = None, None

        if document_type in ['CC', 'CE']:
            query = {"doc": document, "typedoc": document_type, "fechaE": expedition_date}
        elif document_type in ['PP', 'PEP']:
            query = {"doc": document, "typedoc": document_type}
        else:
            _logger.error("****** ERROR: Invalid document type. ******")
            raise ValidationError(f"ERROR: Document type {document_type} not allowed.")

        if query:
            response = self.request_tusdatos_api('launch', query)
        else:
            _logger.error(f"****** ERROR: Invalid query {query}. ******")
            raise ValidationError(f"ERROR: Invalid query {query}.")
        
        
        _logger.error(f"****** PROCCESS: process detail {response}. ******")
        if response and response.get('jobid'):
            response.update({'process_id': response['jobid']})
        elif response and response.get('id'):
            response.update({'process_id': response['id']})
        elif response and response.get('error'):
            response.update({'error': response['error']})
        return response

    def personal_data_approval(self, process_id: str) -> bool:
        """En este endpoint se realizan las peticiones para iniciar la consulta sobre 
        el documento deseado indicando su tipo (CC, CE, NIT, PP, NOMBRE). La consulta
        se realiza en base al perfil asignado al usuario.
        Si la consulta ya fue realizada previamente tendrá una respuesta diferente,
        aplica para el caso de consultas de cédulas consultadas en los últimos 15 días.

        Args: 
            process_id: identificador de la consulta a TusDatos.co (admite dos formatos
            para consulta de resultados por los endpoint /api/results, /api/report_json)

        Return:
            Si la persona esta reportada en la ONU o en la OFAC tendrá False, True en 
            caso contrario.
        """
        approval = False
        validation, endpoint = None, None
        query_type = '-' in process_id

        if query_type:
            _logger.error('results')
            endpoint = 'results'
            results_query = {'jobid': process_id}
            validation = self.request_tusdatos_api(endpoint, results_query)
        else:
            _logger.error('report_json')
            endpoint = 'report_json'
            results_query = {'id': process_id}
            validation = self.request_tusdatos_api(endpoint, results_query)

        if validation:
            
            if 'estado' in validation and validation['estado'] == 'error, tarea no valida':
                _logger.error("****** ERROR: tarea no valida. ******")
            else:
                _logger.error("****** REALIZANDO VALIDACIÓN EN LISTAS. ******")
                #_logger.error(validation)
                #_logger.error(process_id)
                if endpoint == 'results':
                    approval = not (validation['LISTA_ONU'] or validation['OFAC'])
                elif endpoint == 'report_json':
                    #approval = not (validation['ofac'] or validation['lista_onu'] or validation['lista_ofac'])
                    approval = not (validation['ofac'] or validation['lista_onu'])
        else:
            # TODO: add id to sale_order for queue validation process
            _logger.error("****** ERROR: Approbation not processed. ******")
        approval_data = (approval, validation)
        return approval_data
