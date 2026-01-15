from neo4j import GraphDatabase
import os

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")

        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    # -------------------------
    # GET EMPLOYEE CONTEXT
    # -------------------------
    def get_user_context(self, employee_id: str):
        query = """
        MATCH (e:Employee {id:$id})
        OPTIONAL MATCH (e)-[:WORKS_IN]->(d:Department)
        OPTIONAL MATCH (e)-[:REPORTS_TO]->(m:Manager)
        OPTIONAL MATCH (e)-[:MENTORED_BY]->(t:Mentor)
        OPTIONAL MATCH (e)-[:STUDIED_AT]->(c:College)
        OPTIONAL MATCH (e)-[:HAS_TYPE]->(et:EmploymentType)
        RETURN 
            e.name AS name,
            d.name AS department,
            m.name AS manager,
            t.name AS mentor,
            c.name AS college,
            et.name AS employment_type
        """

        with self.driver.session() as session:
            res = session.run(query, id=employee_id)
            record = res.single()

            if not record:
                return None

            return dict(record)

    # -------------------------
    # LIST USERS BY ROLE
    # -------------------------
    def list_people_by_role(self, role: str):
        with self.driver.session() as session:

            if role in ["intern", "full_time"]:
                q = """
                MATCH (e:Employee)-[:HAS_TYPE]->(t:EmploymentType {name:$role})
                RETURN e.id AS id, e.name AS name
                ORDER BY e.id
                """
                res = session.run(q, role=role)

            elif role == "manager":
                q = """
                MATCH (m:Manager)
                RETURN m.id AS id, m.name AS name
                ORDER BY m.id
                """
                res = session.run(q)

            elif role == "mentor":
                q = """
                MATCH (m:Mentor)
                RETURN m.id AS id, m.name AS name
                ORDER BY m.id
                """
                res = session.run(q)

            else:
                return []

            return [dict(r) for r in res]