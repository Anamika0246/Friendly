import mongoose from 'mongoose';

const MediaAssetSchema = new mongoose.Schema(
  {
    ownerId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
    type: { type: String, enum: ['image', 'video'], required: true },
    r2Key: { type: String, required: true },
    url: { type: String },
    sizeBytes: { type: Number },
    mimeType: { type: String },
    width: { type: Number },
    height: { type: Number },
    durationSec: { type: Number },
    status: { type: String, enum: ['processing', 'ready', 'blocked'], default: 'processing', index: true },
  },
  { timestamps: { createdAt: true, updatedAt: false } }
);

MediaAssetSchema.index({ ownerId: 1, createdAt: -1 });

export default mongoose.model('MediaAsset', MediaAssetSchema);
