import json
import re
import socket
from time import sleep
from typing import Callable, Optional, TypeVar

import rdflib
import requests
from rdflib import Graph
from requests.exceptions import ChunkedEncodingError, SSLError
from requests_html import HTMLSession
from urllib3.exceptions import MaxRetryError, NewConnectionError

from Colors import printc
from Times import elapsed_minutes, now

T = TypeVar("T")
E = TypeVar("E")
json_base = list[dict[T, E]]
json_T = dict[T, E]


def to_correct_json(string) -> str:
    """ ex """
    # json_string = str(string).replace("True", "\"True\"").replace("False", "\"False\"").replace("\n", "").replace("\\", "")
    json_string = re.sub(r"(?<=[{,])(.*?):('?)(.*?)('?)(((?<='),)|},{|})", r""""\1":"\3"\5""", string)
    return json_string
    # return str(string).replace("True", "\"True\"").replace("False", "\"False\"").replace("'", "\"").replace("\\", "\\\\")


def text_to_json(json_text: str) -> json_base:
    correct_json = to_correct_json(json_text)
    return json.loads(correct_json)


def url_to_json(url: str, timelimit=1) -> Optional[json_T]:
    html_session = HTMLSession()
    try:
        start = now()
        json_value = None
        while True:
            try:
                if elapsed_minutes(start) >= timelimit:
                    return None
                html_result_text = html_session.get(url)
                html_result_text = html_result_text.text
                if "503 Service Unavailable" in html_result_text or "<Response [403]>" in html_result_text:
                    print("url_to_json error: err Response in html_result_text")
                    sleep(5)
                    continue
                json_value = text_to_json(html_result_text)
                break
            except (ChunkedEncodingError, ConnectionError, NewConnectionError, socket.gaierror, json.decoder.JSONDecodeError,
                    requests.exceptions.ConnectTimeout):
                printc("url_to_json ChunkedEncodingError", background_color="red")
                sleep(2)
                return url_to_json(url)
        return json_value
    except MaxRetryError or SSLError:
        return None


def call_request_api(base_urls: list[str], *start_with, parameters_n_values=None):
    args = ""
    if parameters_n_values is not None:
        args = "&".join((arg + "=" + value for (arg, value) in list(parameters_n_values.items()) if value is not None))
    api_call_url = ""
    for api_call_url in base_urls:
        # try:
        api_call_url += "/" + "/".join(start_with)
        if parameters_n_values is not None:
            api_call_url += "?{}".format(args)
        # except:
        #     continue
        break
    print(api_call_url)
    all_asset_price = url_to_json(api_call_url)
    return all_asset_price


def is_json(txt):
    try:
        json.loads(to_correct_json(txt))
        return True
    except ValueError:  # update
        return False


def json_base_to_json_ok(dictionaries: json_base | dict,
                         keys_aim: list[T],
                         keys_path_to_start: list[T] = None,
                         condition: Callable[[json_T], bool] = None,
                         doublons=True) -> json_T:
    """
    On remplace les indices de la liste de base en la transformant en un dictionnaire où
    les clefs seront les valeurs associées à la clef donnée en paramètre des dictionnaires de la liste.
    S'il y a plusieurs keys, tous les champs doivent avoir le même pattern
    """
    result = {}
    if keys_path_to_start is not None:
        for key in keys_path_to_start:
            dictionaries = dictionaries[key]
    if type(dictionaries) is dict:
        dictionaries = [dictionaries]
    for dictionary in dictionaries:
        key_cursor = dictionary
        for k in keys_aim[:-1]:
            key_cursor = key_cursor[k]
        key = key_cursor[keys_aim[-1]]
        if condition is not None and not condition(dictionary):
            continue
        if doublons and key in result:
            if type(result[key]) is not list:
                result[key] = [result[key]]
            result[key].append(dictionary)
        else:
            result[key] = dictionary
    return result


def url_to_json_ok(url: str,
                   keys: list[T],
                   keys_start: list[T] = None,
                   condition: Callable[[json_T], bool] = None,
                   doublons=True) -> Optional[json_T]:
    json = url_to_json(url)
    if json is None:
        return None
    json_ok = json_base_to_json_ok(json, keys, keys_start, condition, doublons)
    if len(json_ok) == 0:
        raise ValueError("is not json")
    return json_ok


def text_to_json_ok(json_text: str,
                    keys: list[T] | T,
                    keys_start: list[T] = None,
                    condition: Callable[[json_T], bool] = None,
                    doublons=True) -> json_T:
    return json_base_to_json_ok(text_to_json(json_text), keys, keys_start, condition, doublons)


def obj_to_json(obj: object) -> json_T:
    return json.dumps(obj)


def json_to_obj(js: json_T) -> object:
    return json.loads(js)


def rdf_to_json(url):

    import json
    def aux():
        url = ""
        result = rdf_to_json(url)
        if result:
            print(json.dumps(result, indent=2))
            with open('output.json', 'w') as f:
                json.dump(result, f, indent=2)

    g = Graph()
    try:
        for format_type in ['xml', 'turtle', 'n3', 'nt', 'json-ld']:
            try:
                g.parse(url, format=format_type)
                break
            except:
                continue
        data = {}
        for subj, pred, obj in g:
            subject = str(subj)
            if subject not in data:
                data[subject] = {}
            predicate = str(pred)
            if predicate not in data[subject]:
                data[subject][predicate] = []
            if isinstance(obj, rdflib.URIRef):
                obj_value = str(obj)
            elif isinstance(obj, rdflib.Literal):
                obj_value = str(obj)
            else:
                obj_value = str(obj)
            data[subject][predicate].append(obj_value)
        return data
    except Exception as e:
        print(f"Error processing RDF: {e}")
        return None

if __name__ == '__main__':
    # asset_amount = call_request_api(["https://wax.light-api.net/api"], "account", "wax", "b4nvi.wam")
    # asset_amount = json_base_to_json_ok(asset_amount, ["currency"], ["balances"])
    # print(asset_amount)
    print(obj_to_json((dict(zip(("a", "b", "c"), (1, 2, 3))))))
