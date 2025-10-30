import React from 'react';
import { useTranslation } from 'react-i18next';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary:', error, errorInfo);
  }

  render() {
    const { t } = this.props;
    if (this.state.hasError) {
      return <div className="p-4 text-red-500">{t('error')}</div>;
    }
    return this.props.children;
  }
}

export default function WrappedErrorBoundary({ children }) {
  const { t } = useTranslation();
  return <ErrorBoundary t={t}>{children}</ErrorBoundary>;
}
