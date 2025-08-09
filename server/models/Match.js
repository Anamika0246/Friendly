import mongoose from 'mongoose';

const MatchSchema = new mongoose.Schema(
  {
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
    candidateUserId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    score: { type: Number, required: true },
    source: { type: String, default: 'pinecone:query' },
    status: { type: String, enum: ['suggested', 'hidden'], default: 'suggested' },
  },
  { timestamps: { createdAt: true, updatedAt: false } }
);

// Indexes
MatchSchema.index({ userId: 1, score: -1 });
MatchSchema.index({ createdAt: -1 });

export default mongoose.model('Match', MatchSchema);
