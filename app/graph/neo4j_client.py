from neo4j import GraphDatabase
from app.config import settings

driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password)
)


def close_driver():
    driver.close()


def add_document_node(document_id: int, filename: str):
    with driver.session() as session:
        session.run(
            """
            MERGE (d:Document {id: $document_id})
            SET d.filename = $filename
            """,
            document_id=document_id,
            filename=filename,
        )


def add_clause_node(document_id: int, clause_type: str, risk_level: str, content: str):
    with driver.session() as session:
        session.run(
            """
            MATCH (d:Document {id: $document_id})
            CREATE (c:Clause {
                clause_type: $clause_type,
                risk_level: $risk_level,
                content: $content
            })
            CREATE (d)-[:HAS_CLAUSE]->(c)
            """,
            document_id=document_id,
            clause_type=clause_type,
            risk_level=risk_level,
            content=content[:500],  # keep graph nodes lightweight
        )


def get_document_graph(document_id: int):
    """Returns nodes and edges for a document's knowledge graph, for API/frontend consumption."""
    with driver.session() as session:
        result = session.run(
            """
            MATCH (d:Document {id: $document_id})-[:HAS_CLAUSE]->(c:Clause)
            RETURN d.id AS doc_id, d.filename AS filename,
                   c.clause_type AS clause_type, c.risk_level AS risk_level
            """,
            document_id=document_id,
        )
        nodes = []
        edges = []
        doc_added = False
        for record in result:
            if not doc_added:
                nodes.append({"id": f"doc_{record['doc_id']}", "label": record["filename"], "type": "document"})
                doc_added = True
            clause_node_id = f"clause_{record['doc_id']}_{record['clause_type']}"
            nodes.append({
                "id": clause_node_id,
                "label": record["clause_type"],
                "type": "clause",
                "risk_level": record["risk_level"],
            })
            edges.append({"source": f"doc_{record['doc_id']}", "target": clause_node_id, "relation": "HAS_CLAUSE"})

        return {"nodes": nodes, "edges": edges}