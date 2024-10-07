# from loguru import logger
# from magic_bi.config.neo4j_config import Neo4jConfig
# from neomodel import StructuredNode, StringProperty, JSONProperty, Relationship, config
# from loguru import logger
#
# # 配置数据库连接
#
#
# # 定义节点类
# class Entity(StructuredNode):
#     entity_id = StringProperty(unique_index=True)
#     properties = JSONProperty()
#
# # 定义关系类
# class Relation(StructuredNode):
#     relation_id = StringProperty(unique_index=True)
#     type = StringProperty()
#     properties = JSONProperty()
#
# class Neo4jAdapter:
#     def init(self, neo4j_config: Neo4jConfig) -> int:
#         config.DATABASE_URL = neo4j_config.uri
#
#         logger.debug("init suc")
#         return 0
#
#     def add_entity(self, entity):
#         try:
#             new_entity = Entity(id=entity['id'], properties=entity['properties']).save()
#             logger.debug("Entity added with ID {}", entity['id'])
#             return new_entity
#         except Exception as e:
#             logger.error("Failed to add entity: {}", e)
#
#     def add_relation(self, start_entity_id: str, end_entity_id: str, relation):
#         try:
#             start_entity = Entity.nodes.get(id=start_entity_id)
#             end_entity = Entity.nodes.get(id=end_entity_id)
#             relation_obj = start_entity.relation.connect(end_entity, {'id': relation['id'], 'type': relation['type'], 'properties': relation['properties']})
#             logger.debug("Relation added between {} and {} with ID {}", start_entity_id, end_entity_id, relation['id'])
#             return relation_obj
#         except Exception as e:
#             logger.error("Failed to add relation: {}", e)
#
#     def delete_entity(self, entity_id: str):
#         try:
#             entity = Entity.nodes.get(id=entity_id)
#             entity.delete()
#             logger.debug("Entity with ID {} deleted", entity_id)
#         except Entity.DoesNotExist:
#             logger.warning("Entity with ID {} does not exist", entity_id)
#
#     def delete_relation(self, relation_id: str):
#         try:
#             relation = Relation.nodes.get(id=relation_id)
#             relation.delete()
#             logger.debug("Relation with ID {} deleted", relation_id)
#         except Relation.DoesNotExist:
#             logger.warning("Relation with ID {} does not exist", relation_id)
#
#     def delete_graph(self, graph_id: str):
#         try:
#             entities = Entity.nodes.filter(properties__graph_id=graph_id)
#             for entity in entities:
#                 entity.delete()
#             logger.debug("Graph with ID {} deleted", graph_id)
#         except Exception as e:
#             logger.error("Failed to delete graph: {}", e)

# Example usage:
# adapter = Neo4jAdapter()
# adapter.add_entity({"id": "123", "properties": {"name": "John", "graph_id": "001"}})
# adapter.delete_entity("123")
# adapter.close()

