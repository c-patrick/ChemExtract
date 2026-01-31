export type DocumentResponse = {
    id: number;
    status: "pending" | "processing" | "parsed" | "failed";
};

export type ReactionResponse = {
    id: number;
    document_id: number;
    summary: string;
    confidence_score: number;
    parser_version: string;
};