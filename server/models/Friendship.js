import mongoose from 'mongoose';

const FriendshipSchema = new mongoose.Schema(
  {
    userA: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    userB: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    status: { type: String, enum: ['pending', 'accepted', 'blocked'], default: 'pending', index: true },
    requestedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  },
  { timestamps: true }
);

// Unique pair index (order independent)
FriendshipSchema.index(
  { userA: 1, userB: 1 },
  {
    unique: true,
    partialFilterExpression: { userA: { $type: 'objectId' }, userB: { $type: 'objectId' } },
  }
);

export default mongoose.model('Friendship', FriendshipSchema);
