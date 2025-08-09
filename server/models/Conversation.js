import mongoose from 'mongoose';

const ConversationSchema = new mongoose.Schema(
  {
    memberIds: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User', index: true }],
    type: { type: String, enum: ['dm', 'group'], default: 'dm' },
    lastMessageAt: { type: Date },
  },
  { timestamps: { createdAt: true, updatedAt: false } }
);

ConversationSchema.index({ memberIds: 1 }); // multikey
ConversationSchema.index({ lastMessageAt: -1 });

export default mongoose.model('Conversation', ConversationSchema);
