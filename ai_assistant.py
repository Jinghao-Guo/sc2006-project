"""
AI Assistant with RAG (Retrieval-Augmented Generation) using Gemini API
Retrieves data from HDB database and provides intelligent responses
"""

import os
import google.generativeai as genai
from Database import database


class AIAssistant:
    """AI Assistant with RAG capabilities using Gemini API"""

    def __init__(self, api_key=None, model_name=None):
        """Initialize the AI Assistant with Gemini API"""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in environment variables."
            )

        # Configure Gemini API
        genai.configure(api_key=self.api_key)

        # Initialize the model
        # Supported models: "gemini-1.5-flash-latest", "gemini-1.5-pro-latest", "gemini-pro"
        self.model_name = model_name or os.environ.get(
            "GEMINI_MODEL", "gemini-2.5-flash"
        )
        self.model = genai.GenerativeModel(self.model_name)

        # System prompt for the AI assistant
        self.system_prompt = """You are an intelligent HDB (Housing Development Board) property assistant in Singapore. 
You help users find and understand HDB flat information based on their queries.

You have access to a database of HDB resale flats with the following information:
- Town (location in Singapore)
- Flat Type (e.g., 2 ROOM, 3 ROOM, 4 ROOM, 5 ROOM, EXECUTIVE)
- Block and Street Name (address)
- Storey Range (e.g., 01 TO 03, 04 TO 06)
- Floor Area (in square meters)
- Flat Model (e.g., Improved, Model A, Premium Apartment)
- Lease Commence Date (year the lease started)
- Resale Price (in Singapore Dollars)

When answering questions:
1. Be helpful and conversational
2. Provide specific details from the database when available
3. Suggest relevant properties based on user preferences
4. Explain pricing trends and comparisons when asked
5. Give advice on property selection based on data
6. If you don't have enough information, ask clarifying questions

Always format prices with commas and currency (SGD $).
Always mention specific locations (town, street) when discussing properties.
"""

    def retrieve_context(self, query):
        """
        Retrieve relevant data from the database based on the query
        This is the RAG (Retrieval) part - uses LLM to extract search parameters
        """
        context = []

        # Use LLM to extract search parameters from the query
        extraction_prompt = """You are a search parameter extractor for HDB property queries.
Analyze the user's query and extract the following information in JSON format:

Available towns: ANG MO KIO, BEDOK, BISHAN, BUKIT BATOK, BUKIT MERAH, BUKIT PANJANG, BUKIT TIMAH, 
CENTRAL AREA, CHOA CHU KANG, CLEMENTI, GEYLANG, HOUGANG, JURONG EAST, JURONG WEST, 
KALLANG/WHAMPOA, MARINE PARADE, PASIR RIS, PUNGGOL, QUEENSTOWN, SEMBAWANG, SENGKANG, 
SERANGOON, TAMPINES, TOA PAYOH, WOODLANDS, YISHUN

Available flat types: 2 ROOM, 3 ROOM, 4 ROOM, 5 ROOM, EXECUTIVE

Return a JSON object with these fields:
{
    "town": "exact town name from the list above or null if not mentioned",
    "flat_type": "exact flat type from the list above or null if not mentioned"
}

User query: """ + query + """

Respond with ONLY the JSON object, no other text."""

        try:
            # Use LLM to extract parameters
            extraction_response = self.model.generate_content(extraction_prompt)
            response_text = extraction_response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            # Parse the JSON response
            import json
            extracted_params = json.loads(response_text)
            
            town_filter = extracted_params.get("town")
            flat_type_filter = extracted_params.get("flat_type")
            
        except Exception as e:
            # Fallback to empty filters if LLM extraction fails
            print(f"LLM extraction failed: {str(e)}, using empty filters")
            town_filter = None
            flat_type_filter = None

        # Search the database
        try:
            # Get relevant flats based on filters
            flats = database.search_flats(
                query="",
                town=town_filter or "",
                flat_type=flat_type_filter or "",
                limit=10,
                offset=0,
            )

            if flats:
                context.append(f"Found {len(flats)} relevant properties:\n")
                for i, flat in enumerate(flats, 1):
                    flat_dict = dict(flat)
                    context.append(
                        f"\n{i}. Property in {flat_dict['town']}"
                        f"\n   - Type: {flat_dict['flat_type']}"
                        f"\n   - Address: Block {flat_dict['block']}, {flat_dict['street_name']}"
                        f"\n   - Storey: {flat_dict['storey_range']}"
                        f"\n   - Floor Area: {flat_dict['floor_area_sqm']} sqm"
                        f"\n   - Model: {flat_dict['flat_model']}"
                        f"\n   - Lease Started: {flat_dict['lease_commence_date']}"
                        f"\n   - Resale Price: SGD ${flat_dict['resale_price']:,.2f}"
                    )

                # Add statistics if available
                prices = [dict(flat)["resale_price"] for flat in flats]
                if prices:
                    avg_price = sum(prices) / len(prices)
                    min_price = min(prices)
                    max_price = max(prices)
                    context.append(
                        f"\n\nPrice Statistics:"
                        f"\n- Average: SGD ${avg_price:,.2f}"
                        f"\n- Range: SGD ${min_price:,.2f} - SGD ${max_price:,.2f}"
                    )
            else:
                context.append(
                    "No specific properties found matching the exact criteria. "
                    "I'll provide general information based on your query."
                )

        except Exception as e:
            context.append(f"Error retrieving data: {str(e)}")

        return "\n".join(context)

    def chat(self, user_query, conversation_history=None):
        """
        Main chat function with RAG

        Args:
            user_query: The user's question
            conversation_history: Optional list of previous messages

        Returns:
            AI response as a string
        """
        # Retrieve relevant context from database
        retrieved_context = self.retrieve_context(user_query)

        # Build the full prompt
        full_prompt = f"""{self.system_prompt}

DATABASE CONTEXT:
{retrieved_context}

USER QUERY: {user_query}

Please provide a helpful response based on the database context above and your knowledge about HDB properties in Singapore.
"""

        # If there's conversation history, include it
        if conversation_history:
            conversation_text = "\n".join(
                [
                    f"{'User' if i % 2 == 0 else 'Assistant'}: {msg}"
                    for i, msg in enumerate(conversation_history)
                ]
            )
            full_prompt = (
                f"PREVIOUS CONVERSATION:\n{conversation_text}\n\n" + full_prompt
            )

        try:
            # Generate response using Gemini
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def ask_about_flat(self, flat_id):
        """
        Get AI insights about a specific flat

        Args:
            flat_id: The database ID of the flat

        Returns:
            AI analysis of the flat
        """
        try:
            flat = database.query_id(flat_id)
            if not flat:
                return "Flat not found in database."

            flat_dict = dict(flat)

            # Create detailed context about the flat
            context = f"""
Property Details:
- Location: {flat_dict['town']}, Block {flat_dict['block']}, {flat_dict['street_name']}
- Type: {flat_dict['flat_type']}
- Storey: {flat_dict['storey_range']}
- Floor Area: {flat_dict['floor_area_sqm']} sqm
- Model: {flat_dict['flat_model']}
- Lease Commenced: {flat_dict['lease_commence_date']}
- Resale Price: SGD ${flat_dict['resale_price']:,.2f}
"""

            prompt = f"""{self.system_prompt}

SPECIFIC PROPERTY:
{context}

Please provide a comprehensive analysis of this property including:
1. Location advantages
2. Value assessment (is the price reasonable?)
3. Remaining lease considerations
4. Size and layout suitability
5. Overall recommendation

Be specific and data-driven in your analysis.
"""

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"Error analyzing flat: {str(e)}"

    def compare_flats(self, flat_id1, flat_id2):
        """
        Compare two flats and provide AI insights

        Args:
            flat_id1: First flat ID
            flat_id2: Second flat ID

        Returns:
            Comparative analysis
        """
        try:
            flat1 = database.query_id(flat_id1)
            flat2 = database.query_id(flat_id2)

            if not flat1 or not flat2:
                return "One or both flats not found in database."

            flat1_dict = dict(flat1)
            flat2_dict = dict(flat2)

            context = f"""
PROPERTY 1:
- Location: {flat1_dict['town']}, Block {flat1_dict['block']}, {flat1_dict['street_name']}
- Type: {flat1_dict['flat_type']}
- Floor Area: {flat1_dict['floor_area_sqm']} sqm
- Storey: {flat1_dict['storey_range']}
- Model: {flat1_dict['flat_model']}
- Lease Started: {flat1_dict['lease_commence_date']}
- Price: SGD ${flat1_dict['resale_price']:,.2f}

PROPERTY 2:
- Location: {flat2_dict['town']}, Block {flat2_dict['block']}, {flat2_dict['street_name']}
- Type: {flat2_dict['flat_type']}
- Floor Area: {flat2_dict['floor_area_sqm']} sqm
- Storey: {flat2_dict['storey_range']}
- Model: {flat2_dict['flat_model']}
- Lease Started: {flat2_dict['lease_commence_date']}
- Price: SGD ${flat2_dict['resale_price']:,.2f}
"""

            prompt = f"""{self.system_prompt}

COMPARISON REQUEST:
{context}

Please provide a detailed comparison of these two properties covering:
1. Price comparison and value for money
2. Location advantages/disadvantages
3. Size and layout differences
4. Remaining lease comparison
5. Overall recommendation - which is better and why?

Be objective and consider different buyer profiles (e.g., families, singles, investors).
"""

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"Error comparing flats: {str(e)}"


# Create a singleton instance
ai_assistant = None


def get_ai_assistant():
    """Get or create the AI assistant instance"""
    global ai_assistant
    if ai_assistant is None:
        ai_assistant = AIAssistant()
    return ai_assistant
