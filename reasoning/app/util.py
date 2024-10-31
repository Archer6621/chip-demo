from rdflib import Graph, Namespace, URIRef, Literal
from app.reason_question import reason_question
from app.reason_advice import reason_advice
from flask import current_app

import requests


# Function to convert a JSON triple to RDF format
def json_triple_to_rdf(triple):
    # Define namespaces
    user_kg = Namespace("http://www.semanticweb.org/aledpro/ontologies/2024/2/userKG#")

    # Create an RDF graph
    g = Graph()
    g.bind("userKG", user_kg)

    # Extract subject, predicate, and object from the JSON data
    subject = triple.get("subject")
    predicate = triple.get("predicate")
    obj = triple.get("object")
    current_app.logger.debug(f"triple: sub:{subject}, pred:{predicate}, obj:{obj}")

    # Construct subject, predicate, and object URIs
    subject_uri = user_kg[URIRef(subject.replace(" ", ""))]
    predicate_uri = user_kg[URIRef(predicate)]
    if isinstance(obj, (int, float)):
        object_uri = Literal(obj)
    else:
        object_uri = user_kg[URIRef(obj.replace(" ", ""))]

    # Add the triple to the graph
    g.add((subject_uri, predicate_uri, object_uri))

    # Serialize the graph to Turtle format and return
    return g.serialize(format="turtle")


# Function to upload RDF data to GraphDB
def upload_rdf_data(rdf_data, content_type='application/x-turtle'):
    """
    Upload RDF data to a GraphDB repository using the REST API.

    :param rdf_data: RDF data in string format (Turtle, RDF/XML, etc.)
    :param content_type: MIME type of the RDF data (default is Turtle)
    :return: Response object
    """
    headers = {
        'Content-Type': content_type
    }

    # Construct the full endpoint URL
    url = current_app.config.get('knowledge_url', None)

    # TODO: Improve consistency in return types
    #       Maybe we should only return what we want and throw exceptions in the other cases
    #       These exceptions can be caught, and then handled appropriately in the route itself via status codes
    if not url:
        return "No address configured for knowledge database", 503
    endpoint = f"{url}/statements"

    # Send a POST request to upload the RDF data
    response = requests.post(endpoint, data=rdf_data, headers=headers)

    if not response.ok:
        current_app.logger.error(f"Failed to upload RDF data: {response.status_code}, Response: {response.text}")
    else:
        current_app.logger.info('Successfully uploaded RDF data.')

    return response


def reason():
    response = reason_advice()
    current_app.logger.info(f"advice response: {response}")

    reason_type = 'A'
    if (not response or not response['data']):
        current_app.logger.info("Could not give advice, asking question instead")
        reason_type = 'Q'
        response = reason_question()

    # SEND REASONING RESULT
    current_app.logger.info(f"reasoning result: {response}")
    return {"type": reason_type, "data": response}

