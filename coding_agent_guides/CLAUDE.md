# Vectara API
Vectara is an end-to-end platform designed to empower product builders by embedding powerful Generative AI features into their applications.
Vectara supports an API enabling full access to its features primarily focused around Retrieval Augmented Generation (RAG) capabilities, allowing businesses to integrate conversational AI and question-answering functionalities safely and affordably.

Vectara supports REST API endpoints, using GET and POST requests for the most common operations.
Use APIv2 only (do not use APIv1)

It follows HTTP status code conventions (2xx indicating a successful response, 4xx indicating an error in the request, and 5xx indicating a server error).
In the case of a 4xx error, the response object will likely include a "messages" key, which is a list of strings indicating the errors of the request.

You can create a corpus in Vectara that would hold your data, or use an existing corpus if you know the corpus key.

The most common API endpoints used are the query APIs (for single or multiple corpora), the index and file upload APIs (for adding new documents to corpora), the document APIs (for retrieving, listing, and summarizing documents in a corpus), the corpus APIs (for retrieving metadata about a corpus), and the factual consistency APIs.

Every request will require an API key as a credential in the header of the request.
You will also need to specify the corpus key(s) for the corpora that you want to perform the operation on.

## Metadata

Many API endpoints have a metadata_filter argument which allows you to filter the documents by their associated metadata.
Vectara has a specific structure for how these filters should be expressed.

This page contains an overview about the different types of metadata filters: https://docs.vectara.com/docs/learn/metadata-search-filtering/filter-overview

Each document has some default metadata filters that are automatically produced. You can find them here: https://docs.vectara.com/docs/learn/metadata-search-filtering/ootb-metadata-filters

There is a fixed set of functions and operators that can be used with metadata filter expressions, which you can learn about on this page: https://docs.vectara.com/docs/api-reference/search-apis/sql/func-opr

## Query APIs

The query endpoints allow you to perform RAG across one or more corpora in a user account, retrieving the most relevant documents and generating a response to the query using an LLM.
The API request includes 2 main groups of parameters:

1.  Search parameters that allow you to filter data by associated document or part metadata, a hybrid search parameter (how much to use keyword vs. neural search), how to rerank results after the initial retrieval, and how much additional context to provide with the matching texts.
2.  Summarization parameters that control the generated response by the LLM, including the LLM model, a custom prompt, the maximum number of search results that should be used to generate the response, the response language, how to present citations, and whether to include the factual consistency score with the query results (Factual Consistency Score is a metric that evaluates the likelihood of AI-generated summaries being factually accurate based on the retrieved data; it is available for responses generated in English, German, French, Portuguese, Spanish, Arabic, Chinese-Simplified, Korean, Russian, Japanese, and Hindi).

Custom prompts must follow a specific template which is specified on this page: https://docs.vectara.com/docs/prompts/vectara-prompt-engine.

When creating these prompts, you can access certain variables and functions which can be found on this page: https://docs.vectara.com/docs/prompts/custom-prompts-with-metadata

If you want to query a single Vectara corpus, you should use the Advanced Single Corpus Query endpoint.
The documentation for this endpoint can be found on this page: https://docs.vectara.com/docs/rest-api/query-corpus

If you want to query multiple corpora at once, use the Multiple Corpora Query endpoint. Documentation is available here: https://docs.vectara.com/docs/rest-api/query

## Index and File Upload APIs

If you need to add a new document to a Vectara corpus, you can use the Index and File Upload API endpoints.

The File Upload API allows you to upload PDF and Microsoft Word files as well as other text documents.
The supported file types can be found on this page: https://docs.vectara.com/docs/api-reference/indexing-apis/file-upload/file-upload-filetypes

Vectara will handle the chunking and indexing of these documents for you so that it is optimized for high-quality retrieval.
The documentation for this endpoint can be found on this page: https://docs.vectara.com/docs/rest-api/upload-file

If you have all of the text for a document and want more control over how the document is represented in the Vectara corpus,
you can index the document using the add document API. This supports two kinds of documents:
1.  A structured document where you provide the structure of the document (such as the different sections and subsections of the document).
2.  A core document where you provide a more granular structure, explicitly defining each document part as it should be represented when it is stored by Vectara.
    this gives you the most control over how your document is stored in a Vectara corpus.

To learn more about these document types, check out these pages about [Structured Document Objects](https://docs.vectara.com/docs/api-reference/indexing-apis/indexing#structured-document-object-definition) and [Core Document Objects](https://docs.vectara.com/docs/api-reference/indexing-apis/indexing#core-document-object-definition)

You can find the documentation for indexing a document in a corpus here: https://docs.vectara.com/docs/rest-api/create-corpus-document

## Document APIs

The document API endpoints allow you to get information about documents in a Vectara corpus, including the full document, its associated metadata, and a summary of its contents.

To get a list of the documents in a corpus, you can use the List Documents endpoint. This allows you to get the document ids and metadata associated with each document in a corpus.
If a document has tables, you can also see their contents using this endpoint.

You can also filter the list by document metadata.

Making a call to this endpoint may not retrieve all of the documents in the corpus in a single request.
You can use the page_key returned in the metadata of the response for one request to this endpoint as input to another request to get other documents in this corpus.
To get all of the documents in this corpus, you can continue using the page_key from the previous request in the next request until there is no page key in the response.
At this point, you have iterated through all documents in the corpus.

You can find the documentation for this endpoint here: https://docs.vectara.com/docs/rest-api/list-corpus-documents

If you would like to get the full content of a document, you can use the Retrieve Document endpoint.
By providing the document id, you can get the content and metadata for that document.
Documentation for this endpoint is found on this page: https://docs.vectara.com/docs/rest-api/get-corpus-document

If you would like to retrieve a summary of a document, you can use the Summarize Document endpoint.
You are able to choose the LLM used to generate the summary and can give a custom prompt if you would like.
To see the available list of LLMs, use the List LLMs API endpoint: https://docs.vectara.com/docs/rest-api/list-ll-ms

If you want to use an LLM that is not in this list, you can set up a new LLM using the Create LLM endpoint ([Documentation](https://docs.vectara.com/docs/api-reference/llms-apis/create-llm) and [API Reference](https://docs.vectara.com/docs/rest-api/create-llm)).

Refer to the custom prompt documentation provided above to see how to structure prompts.
The documentation for the Summarize Document endpoint is found on this page: https://docs.vectara.com/docs/rest-api/summarize-corpus-document

## Corpus APIs

The corpus APIs allow you to create a new corpus, modify an existing corpus, and get information about a corpus.

To create a new corpus, use the Create Corpus endpoint. Details can be found here: https://docs.vectara.com/docs/rest-api/create-corpus

To update the filter attributes of a corpus, use the Replace Filter Attributes endpoint.
Filter attributes are the metadata fields that can be used to filter search results when querying a corpus.
See this page for the documentation about this endpoint: https://docs.vectara.com/docs/rest-api/replace-filter-attributes

To get information about a corpus, including the name, description, and filter attributes, use the Retrieve Metadata endpoint. Details can be found here: https://docs.vectara.com/docs/rest-api/get-corpus

## Factual Consistency APIs

The factual consistency APIs can be used to determine the factual accuracy of generated responses based on source documents.

The most helpful endpoint among these is the Correct Hallucinations endpoint.
This endpoint can be used to identify information in a generated text that is not supported by the source documents and suggest corrections to resolve the hallucinations.
It requires the generated text and the source documents used to generate that text.
This endpoint is particularly useful after using one of the query APIs, which provide the generated text and accompanying source documents.
The documentation for this endpoint is found on this page: https://docs.vectara.com/docs/rest-api/correct-hallucinations

If you simply want to evaluate the factual accuracy of a generated response, you can use the Evaluate Factual Consistency endpoint,
which returns a value between 0 (generated text is not grounded at all in the source documents) and 1 (generated text contains no hallucinations based on source documents).
Here is the documentation for this endpoint: https://docs.vectara.com/docs/rest-api/evaluate-factual-consistency

## More Information

These are just some of the most useful API endpoints offered by Vectara.

If you need even more capabilities, you can check out Vectara's [full documentation](https://docs.vectara.com/docs/) and [API endpoint references](https://docs.vectara.com/docs/rest-api).
