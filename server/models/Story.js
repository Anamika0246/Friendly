import mongoose from 'mongoose';

const StorySchema = new mongoose.Schema(
  {
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, unique: true, index: true },
    text: { type: String, required: true },
    language: { type: String, default: 'en' },
    vectorId: { type: String, trim: true }, // e.g., user:<userId>
  },
  { timestamps: true }
);

// Indexes
StorySchema.index({ createdAt: 1 });

export default mongoose.model('Story', StorySchema);
