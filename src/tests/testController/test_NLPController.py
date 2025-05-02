import pytest
from unittest import mock
from controllers.NLPController import NLPController
from models.db_schemes import Project, DataChunk


# Création de mock pour les clients externes
@pytest.fixture
def mock_clients():
    vectordb_client = mock.Mock()
    generation_client = mock.Mock()
    embedding_client = mock.Mock()
    template_parser = mock.Mock()

    
    return vectordb_client, generation_client, embedding_client, template_parser


@pytest.fixture
def nlp_controller(mock_clients):
    vectordb_client, generation_client, embedding_client, template_parser = mock_clients
    return NLPController(
        vectordb_client=vectordb_client,
        generartion_client=generation_client,
        embedding_client=embedding_client,
        template_parser=template_parser
    )

# Test de la méthode create_collection_name
def test_create_collection_name(nlp_controller):
    project_id = "123"
    collection_name = nlp_controller.create_collection_name(project_id)
    assert collection_name == "collection_123"


# Test de index_into_vector_db
def test_index_into_vector_db(nlp_controller, mock_clients):

    project = mock.Mock(spec=Project, project_id="123")
    chunks = [mock.Mock(spec=DataChunk, chunk_text="text 1", chunk_metadata="meta 1"),
              mock.Mock(spec=DataChunk, chunk_text="text 2", chunk_metadata="meta 2")]
    chunks_ids = [1, 2]
    
    # Simuler le comportement des clients
    nlp_controller.vectordb_client.create_collection.return_value = None
    nlp_controller.vectordb_client.insert_many.return_value = None
    nlp_controller.embeddings_client.embed_text.return_value = [0.1, 0.2, 0.3]

    result = nlp_controller.index_into_vector_db(
        project=project, chunks=chunks, chunks_ids=chunks_ids
    )

    # Vérification des appels des clients
    nlp_controller.vectordb_client.create_collection.assert_called_once_with(
        collection_name="collection_123",
        embedding_size=3,
        do_reset=False
    )
    nlp_controller.vectordb_client.insert_many.assert_called_once()
    assert result is True


# Test de la méthode answer_rag_question
def test_answer_rag_question(nlp_controller, mock_clients):
    project = mock.Mock(spec=Project, project_id="123")
    query = "What is the best way to learn Python?"

    # Simuler le comportement des clients
    nlp_controller.search_vector_db_collection.return_value = [
        mock.Mock(text="Document 1", metadata={"id": 1}),
        mock.Mock(text="Document 2", metadata={"id": 2})
    ]
    nlp_controller.template_parser.get.return_value = "test prompt"
    nlp_controller.generation_client.generate_text.return_value = "Python is the best way to learn."

    # Tester la méthode
    answer, full_prompt, chat_history = nlp_controller.answer_rag_question(
        project=project, query=query, limit=2
    )

    # Vérification des appels
    nlp_controller.search_vector_db_collection.assert_called_once_with(
        project=project, text=query, limit=2
    )
    nlp_controller.generation_client.generate_text.assert_called_once()

    # Vérification des résultats
    assert answer == "Python is the best way to learn."
    assert "test prompt" in full_prompt

