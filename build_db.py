import chromadb

# Initialize a local database folder named 'resume_vector_db'
db_client = chromadb.PersistentClient(path="./resume_vector_db")

collection = db_client.get_or_create_collection(name="perfect_resume_bullets")

# Synthetic resume data (should be much more)
synthetic_data = [
    "Tech/Software: Engineered a distributed microservices architecture using Python and Docker, reducing system latency by 40% and supporting 10,000+ concurrent users.",
    "Tech/Software: Optimized legacy SQL database queries, decreasing data retrieval time by 60% and saving $5,000 annually in cloud computing costs.",
    "Finance: Managed a $5M portfolio, utilizing advanced Excel financial modeling and Python data analysis to identify market trends, resulting in a 12% YoY return.",
    "Marketing: Directed a cross-channel digital marketing campaign with a $50,000 budget, achieving a 300% ROI and acquiring 25,000 new active leads within Q3.",
    "Management: Led a cross-functional team of 15 engineers and designers using Agile methodologies, delivering the flagship product 2 weeks ahead of schedule and 10% under budget.",
    "Customer Success: Resolved escalated enterprise client issues, maintaining a 98% customer retention rate and generating $1.2M in contract renewals."
]
ids = [f"bullet_{i}" for i in range(len(synthetic_data))]

collection.add(
    documents=synthetic_data,
    ids=ids
)