import mongoose from 'mongoose';

const MessageSchema = new mongoose.Schema(
  {
    conversationId: { type: mongoose.Schema.Types.ObjectId, ref: 'Conversation', required: true, index: true },
    senderId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
    type: { type: String, enum: ['text', 'image', 'video'], default: 'text' },
    text: { type: String },
    mediaId: { type: mongoose.Schema.Types.ObjectId, ref: 'MediaAsset' },
    mediaUrl: { type: String },
    durationSec: { type: Number },
    viewedBy: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
    deletedFor: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
  },
  { timestamps: { createdAt: true, updatedAt: false } }
);

MessageSchema.index({ conversationId: 1, createdAt: 1 });
MessageSchema.index({ senderId: 1, createdAt: 1 });

export default mongoose.model('Message', MessageSchema);
