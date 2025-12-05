import mongoose from 'mongoose';

/**
 * Connect to MongoDB Database
 * Handles connection, error, and disconnection events
 */
const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGO_URI, {
      // These options are no longer needed in Mongoose 6+
      // but keeping them for backward compatibility
    });

    console.log(`\x1b[36m\x1b[1m✅ MongoDB Connected: ${conn.connection.host}\x1b[0m`);

    // Connection success handler
    mongoose.connection.on('connected', () => {
      console.log('✅ Mongoose connected to DB');
    });

    // Connection error handler
    mongoose.connection.on('error', (err) => {
      console.error(`❌ Mongoose connection error: ${err}`.red.bold);
    });

    // Connection disconnected handler
    mongoose.connection.on('disconnected', () => {
      console.log('⚠️  Mongoose disconnected');
    });

  } catch (error) {
    console.error(`\x1b[31m\x1b[1m❌ Error connecting to MongoDB: ${error.message}\x1b[0m`);
    process.exit(1); // Exit with failure
  }
};

// Handle process termination
process.on('SIGINT', async () => {
  await mongoose.connection.close();
  console.log('⚠️  MongoDB connection closed through app termination');
  process.exit(0);
});

export default connectDB;