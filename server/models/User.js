import mongoose from 'mongoose';

const UserSchema = new mongoose.Schema(
  {
    handle: { type: String, required: true, unique: true, index: true, trim: true },
    name: { type: String, trim: true },
    avatarUrl: { type: String, trim: true },
    bio: { type: String, trim: true },
    flags: {
      blocked: { type: Boolean, default: false },
      verified: { type: Boolean, default: false },
    },
  },
  { timestamps: true }
);

// Indexes
UserSchema.index({ createdAt: 1 });

export default mongoose.model('User', UserSchema);
