import mongoose from 'mongoose';

const SnapSchema = new mongoose.Schema(
  {
    senderId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
    recipientIds: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
    mediaId: { type: mongoose.Schema.Types.ObjectId, ref: 'MediaAsset' },
    mediaUrl: { type: String, required: true },
    durationSec: { type: Number, required: true },
    expiresAt: { type: Date, required: true, index: true },
  },
  { timestamps: { createdAt: true, updatedAt: false } }
);

// TTL index to auto-delete expired snaps (ensure MongoDB TTL monitor is enabled)
SnapSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });

export default mongoose.model('Snap', SnapSchema);
