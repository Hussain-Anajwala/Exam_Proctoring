# Exam Proctoring System - Frontend

A comprehensive React frontend application built with TypeScript and Tailwind CSS that provides a user interface for the Unified Exam Proctoring System.

## Features

This frontend application provides interfaces for all 8 exam system tasks:

### 🛡️ Violation Detection
- Real-time violation reporting interface
- Student selection and violation tracking
- Live marksheet display with status indicators
- Export functionality for marksheet data

### 🕐 Clock Synchronization
- Multi-participant clock registration
- Berkeley algorithm simulation
- Real-time synchronization results
- Time comparison visualization

### 🔒 Mutual Exclusion
- Token-based mutual exclusion simulation
- Student request management
- Queue visualization
- Response history tracking

### 📚 Exam Processing
- Interactive exam interface
- Question display with multiple choice options
- Automatic scoring and mark release
- Exam status tracking

### ⚖️ Load Balancing
- Dynamic load balancing visualization
- Submission management
- System status monitoring
- Migration threshold indicators

### 🗄️ Database Management
- Student record management
- Search and filter functionality
- Record updates with 2PC protocol
- Export capabilities

## Technology Stack

- **React 19** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API communication
- **Lucide React** - Beautiful icons
- **Vite** - Fast build tool and dev server

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Python server running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
```bash
cd client_frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/           # React components
│   ├── Layout/          # Layout components (Navbar, Layout)
│   ├── Dashboard/       # Dashboard component
│   ├── ViolationDetection/  # Violation detection interface
│   ├── ClockSync/       # Clock synchronization interface
│   ├── MutualExclusion/ # Mutual exclusion interface
│   ├── ExamProcessing/  # Exam processing interface
│   ├── LoadBalancing/   # Load balancing interface
│   └── Database/        # Database management interface
├── services/            # API service layer
│   └── api.ts          # API client and endpoints
├── types/              # TypeScript type definitions
│   └── index.ts        # All type definitions
├── App.tsx             # Main application component
├── main.tsx            # Application entry point
└── index.css           # Global styles
```

## API Integration

The frontend communicates with the Python backend through REST API endpoints:

- **Base URL**: `http://localhost:8000/api/v1`
- **Proxy**: Configured in `vite.config.ts` for development
- **Error Handling**: Comprehensive error handling with user feedback
- **Loading States**: Loading indicators for all async operations

## Key Features

### Responsive Design
- Mobile-first approach
- Responsive grid layouts
- Touch-friendly interfaces
- Adaptive navigation

### Real-time Updates
- Auto-refresh functionality
- Live status indicators
- Real-time data synchronization
- Background polling for critical data

### User Experience
- Intuitive navigation
- Clear visual feedback
- Error handling with helpful messages
- Loading states and progress indicators

### Data Visualization
- Charts and graphs for system metrics
- Color-coded status indicators
- Progress bars and loading animations
- Interactive data tables

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Style

- TypeScript strict mode enabled
- ESLint configuration for code quality
- Consistent component structure
- Proper error handling patterns

## Deployment

### Environment Variables

Create a `.env` file for environment-specific configuration:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=Exam Proctoring System
```

### Production Build

1. Build the application:
```bash
npm run build
```

2. Serve the `dist` directory with any static file server:
```bash
npx serve dist
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Include error handling
4. Add loading states for async operations
5. Test on multiple screen sizes

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure Python server is running on port 8000
   - Check CORS configuration
   - Verify network connectivity

2. **Build Errors**
   - Clear node_modules and reinstall
   - Check TypeScript errors
   - Verify all dependencies are installed

3. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check for conflicting CSS
   - Verify responsive breakpoints

## License

This project is part of the Exam Proctoring System and follows the same license terms.