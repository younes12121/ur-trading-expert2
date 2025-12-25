"""
AI Predictive Analytics Dashboard
Provides real-time AI insights, predictive analytics, and interactive visualizations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictiveAnalyticsDashboard:
    """AI-powered predictive analytics dashboard"""

    def __init__(self):
        self.dashboard_data = {}
        self.prediction_history = []
        self.performance_metrics = {}
        self.ai_insights = []

    def update_dashboard_data(self, market_data: Dict, predictions: Dict,
                            performance: Dict, ai_insights: List[Dict]):
        """Update dashboard with latest data"""
        timestamp = datetime.now()

        self.dashboard_data = {
            'timestamp': timestamp,
            'market_data': market_data,
            'predictions': predictions,
            'performance': performance,
            'ai_insights': ai_insights
        }

        # Store prediction history for trend analysis
        if predictions:
            self.prediction_history.append({
                'timestamp': timestamp,
                **predictions
            })

            # Keep only last 1000 predictions
            if len(self.prediction_history) > 1000:
                self.prediction_history = self.prediction_history[-1000:]

        # Update performance metrics
        self.performance_metrics.update(performance)

        logger.info(f"Dashboard updated at {timestamp}")

    def generate_market_overview(self) -> Dict:
        """Generate comprehensive market overview with AI insights"""
        if not self.dashboard_data:
            return {'error': 'No dashboard data available'}

        market_data = self.dashboard_data.get('market_data', {})
        predictions = self.dashboard_data.get('predictions', {})

        overview = {
            'timestamp': self.dashboard_data.get('timestamp'),
            'market_summary': self._analyze_market_conditions(market_data),
            'ai_predictions': self._summarize_predictions(predictions),
            'risk_assessment': self._calculate_risk_metrics(market_data),
            'trading_opportunities': self._identify_opportunities(predictions),
            'key_insights': self._generate_key_insights()
        }

        return overview

    def _analyze_market_conditions(self, market_data: Dict) -> Dict:
        """Analyze current market conditions"""
        analysis = {
            'overall_sentiment': 'neutral',
            'volatility_level': 'medium',
            'trend_strength': 'moderate',
            'assets_analyzed': len(market_data.get('assets', {})),
            'market_regime': 'unknown'
        }

        if not market_data.get('assets'):
            return analysis

        # Analyze each asset
        bullish_assets = 0
        bearish_assets = 0
        high_vol_assets = 0
        total_assets = len(market_data['assets'])

        for asset, data in market_data['assets'].items():
            if isinstance(data, dict):
                # Check price momentum
                if data.get('momentum', 0) > 0.01:
                    bullish_assets += 1
                elif data.get('momentum', 0) < -0.01:
                    bearish_assets += 1

                # Check volatility
                if data.get('volatility', 0) > 0.03:
                    high_vol_assets += 1

        # Determine overall sentiment
        if bullish_assets > total_assets * 0.6:
            analysis['overall_sentiment'] = 'bullish'
        elif bearish_assets > total_assets * 0.6:
            analysis['overall_sentiment'] = 'bearish'

        # Determine volatility level
        if high_vol_assets > total_assets * 0.5:
            analysis['volatility_level'] = 'high'
        elif high_vol_assets < total_assets * 0.2:
            analysis['volatility_level'] = 'low'

        # Determine market regime
        if analysis['overall_sentiment'] == 'bullish' and analysis['volatility_level'] == 'low':
            analysis['market_regime'] = 'strong_bull'
        elif analysis['overall_sentiment'] == 'bearish' and analysis['volatility_level'] == 'low':
            analysis['market_regime'] = 'strong_bear'
        elif analysis['volatility_level'] == 'high':
            analysis['market_regime'] = 'volatile'
        else:
            analysis['market_regime'] = 'sideways'

        return analysis

    def _summarize_predictions(self, predictions: Dict) -> Dict:
        """Summarize AI predictions across all assets"""
        if not predictions:
            return {'total_predictions': 0, 'average_confidence': 0}

        total_predictions = len(predictions)
        total_confidence = 0
        bullish_predictions = 0
        bearish_predictions = 0
        high_conf_predictions = 0

        for asset, pred in predictions.items():
            if isinstance(pred, dict):
                confidence = pred.get('confidence', 0)
                total_confidence += confidence

                direction = pred.get('direction', 'neutral')
                if direction == 'bullish':
                    bullish_predictions += 1
                elif direction == 'bearish':
                    bearish_predictions += 1

                if confidence > 80:
                    high_conf_predictions += 1

        return {
            'total_predictions': total_predictions,
            'average_confidence': total_confidence / total_predictions if total_predictions > 0 else 0,
            'bullish_predictions': bullish_predictions,
            'bearish_predictions': bearish_predictions,
            'high_confidence_predictions': high_conf_predictions,
            'prediction_distribution': {
                'bullish': bullish_predictions,
                'bearish': bearish_predictions,
                'neutral': total_predictions - bullish_predictions - bearish_predictions
            }
        }

    def _calculate_risk_metrics(self, market_data: Dict) -> Dict:
        """Calculate comprehensive risk metrics"""
        if not market_data.get('assets'):
            return {'overall_risk': 'unknown', 'diversification_score': 0}

        assets = market_data['assets']
        volatilities = []
        correlations = []

        # Calculate individual asset volatilities
        for asset, data in assets.items():
            if isinstance(data, dict) and 'volatility' in data:
                volatilities.append(data['volatility'])

        # Calculate portfolio risk metrics
        if volatilities:
            avg_volatility = np.mean(volatilities)
            max_volatility = max(volatilities)
            volatility_dispersion = np.std(volatilities)

            # Risk assessment
            if avg_volatility > 0.04:
                risk_level = 'high'
            elif avg_volatility > 0.02:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            # Diversification score (lower dispersion = better diversification)
            diversification_score = max(0, 100 - (volatility_dispersion * 1000))
        else:
            risk_level = 'unknown'
            diversification_score = 0
            avg_volatility = 0

        return {
            'overall_risk': risk_level,
            'average_volatility': avg_volatility,
            'diversification_score': diversification_score,
            'assets_count': len(assets),
            'risk_factors': self._identify_risk_factors(market_data)
        }

    def _identify_risk_factors(self, market_data: Dict) -> List[str]:
        """Identify current risk factors"""
        risk_factors = []

        assets = market_data.get('assets', {})

        # Check for high volatility assets
        high_vol_assets = [asset for asset, data in assets.items()
                          if isinstance(data, dict) and data.get('volatility', 0) > 0.04]

        if high_vol_assets:
            risk_factors.append(f"High volatility in: {', '.join(high_vol_assets[:3])}")

        # Check for correlated movements (simplified)
        if len(assets) > 2:
            risk_factors.append("Potential correlation risk across assets")

        # Market regime risks
        regime = market_data.get('regime', 'unknown')
        if regime == 'volatile':
            risk_factors.append("Market in volatile regime - exercise caution")
        elif regime in ['strong_bear', 'strong_bull']:
            risk_factors.append(f"Strong {regime.split('_')[1]} trend - momentum risk")

        return risk_factors if risk_factors else ["No significant risk factors identified"]

    def _identify_opportunities(self, predictions: Dict) -> List[Dict]:
        """Identify trading opportunities based on AI predictions"""
        opportunities = []

        if not predictions:
            return opportunities

        for asset, pred in predictions.items():
            if not isinstance(pred, dict):
                continue

            confidence = pred.get('confidence', 0)
            direction = pred.get('direction', 'neutral')

            # High confidence bullish signals
            if direction == 'bullish' and confidence > 85:
                opportunities.append({
                    'type': 'high_confidence_bullish',
                    'asset': asset,
                    'confidence': confidence,
                    'direction': direction,
                    'priority': 'high',
                    'description': f"Strong bullish signal for {asset} ({confidence:.1f}% confidence)"
                })

            # High confidence bearish signals
            elif direction == 'bearish' and confidence > 85:
                opportunities.append({
                    'type': 'high_confidence_bearish',
                    'asset': asset,
                    'confidence': confidence,
                    'direction': direction,
                    'priority': 'high',
                    'description': f"Strong bearish signal for {asset} ({confidence:.1f}% confidence)"
                })

            # Medium confidence signals
            elif confidence > 70:
                opportunities.append({
                    'type': 'medium_confidence_signal',
                    'asset': asset,
                    'confidence': confidence,
                    'direction': direction,
                    'priority': 'medium',
                    'description': f"Moderate {direction} signal for {asset} ({confidence:.1f}% confidence)"
                })

        # Sort by confidence
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)

        return opportunities[:10]  # Top 10 opportunities

    def _generate_key_insights(self) -> List[str]:
        """Generate key AI insights for the dashboard"""
        insights = []

        if not self.dashboard_data:
            return ["No data available for insights"]

        # Analyze prediction trends
        if len(self.prediction_history) > 10:
            recent_predictions = self.prediction_history[-10:]
            avg_confidence = np.mean([p.get('confidence', 0) for p in recent_predictions])

            if avg_confidence > 80:
                insights.append("AI confidence is exceptionally high - strong signal environment")
            elif avg_confidence < 60:
                insights.append("AI confidence is low - mixed signal environment, exercise caution")

        # Market regime insights
        market_analysis = self.dashboard_data.get('market_summary', {})
        regime = market_analysis.get('market_regime', 'unknown')

        if regime == 'strong_bull':
            insights.append("Market in strong bullish regime - favor long positions")
        elif regime == 'strong_bear':
            insights.append("Market in strong bearish regime - favor short positions")
        elif regime == 'volatile':
            insights.append("High market volatility - consider reducing position sizes")

        # Performance insights
        performance = self.dashboard_data.get('performance', {})
        if performance.get('win_rate', 0) > 0.7:
            insights.append("Strong recent performance - strategies are effective")
        elif performance.get('win_rate', 0) < 0.5:
            insights.append("Recent performance below average - review strategy parameters")

        return insights if insights else ["Market conditions are stable with no significant insights"]

    def create_dashboard_visualizations(self) -> Dict:
        """Create interactive dashboard visualizations"""
        if not self.dashboard_data:
            return {'error': 'No data available for visualization'}

        visualizations = {
            'market_sentiment_gauge': self._create_sentiment_gauge(),
            'prediction_confidence_chart': self._create_confidence_chart(),
            'performance_timeline': self._create_performance_timeline(),
            'risk_heatmap': self._create_risk_heatmap(),
            'opportunity_radar': self._create_opportunity_radar()
        }

        return visualizations

    def _create_sentiment_gauge(self) -> go.Figure:
        """Create market sentiment gauge chart"""
        market_analysis = self.dashboard_data.get('market_summary', {})
        sentiment = market_analysis.get('overall_sentiment', 'neutral')

        # Convert sentiment to numerical value
        sentiment_values = {'bearish': 25, 'neutral': 50, 'bullish': 75}
        value = sentiment_values.get(sentiment, 50)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': "Market Sentiment"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 33], 'color': "red"},
                    {'range': [33, 66], 'color': "yellow"},
                    {'range': [66, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ))

        return fig

    def _create_confidence_chart(self) -> go.Figure:
        """Create prediction confidence timeline chart"""
        if not self.prediction_history:
            return go.Figure()

        # Extract confidence over time
        timestamps = [p['timestamp'] for p in self.prediction_history[-50:]]  # Last 50 predictions
        confidences = [p.get('confidence', 0) for p in self.prediction_history[-50:]]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=confidences,
            mode='lines+markers',
            name='AI Confidence',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ))

        fig.update_layout(
            title="AI Prediction Confidence Over Time",
            xaxis_title="Time",
            yaxis_title="Confidence (%)",
            yaxis_range=[0, 100]
        )

        return fig

    def _create_performance_timeline(self) -> go.Figure:
        """Create performance metrics timeline"""
        # This would show win rate, profit factor, etc. over time
        # Simplified version for now
        fig = go.Figure()

        # Add performance traces
        performance = self.dashboard_data.get('performance', {})
        if performance:
            metrics = ['win_rate', 'profit_factor', 'sharpe_ratio']
            for metric in metrics:
                if metric in performance:
                    value = performance[metric]
                    fig.add_trace(go.Bar(
                        name=metric.replace('_', ' ').title(),
                        x=[metric.replace('_', ' ').title()],
                        y=[value],
                        marker_color='lightblue'
                    ))

        fig.update_layout(
            title="Current Performance Metrics",
            yaxis_title="Value"
        )

        return fig

    def _create_risk_heatmap(self) -> go.Figure:
        """Create risk assessment heatmap"""
        assets = list(self.dashboard_data.get('market_data', {}).get('assets', {}).keys())
        risk_factors = ['Volatility', 'Correlation', 'Momentum', 'Volume']

        if not assets:
            return go.Figure()

        # Generate mock risk scores (would be calculated from real data)
        np.random.seed(42)
        risk_scores = np.random.rand(len(assets), len(risk_factors)) * 100

        fig = go.Figure(data=go.Heatmap(
            z=risk_scores,
            x=risk_factors,
            y=assets,
            colorscale='RdYlGn_r',  # Red-Yellow-Green reversed
            showscale=True
        ))

        fig.update_layout(
            title="Asset Risk Heatmap",
            xaxis_title="Risk Factor",
            yaxis_title="Asset"
        )

        return fig

    def _create_opportunity_radar(self) -> go.Figure:
        """Create opportunity radar chart"""
        opportunities = self._identify_opportunities(
            self.dashboard_data.get('predictions', {})
        )

        if not opportunities:
            return go.Figure()

        # Group opportunities by type
        opp_types = {}
        for opp in opportunities:
            opp_type = opp['type']
            opp_types[opp_type] = opp_types.get(opp_type, 0) + 1

        categories = list(opp_types.keys())
        values = list(opp_types.values())

        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Trading Opportunities'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) + 1]
                )),
            showlegend=False,
            title="Trading Opportunities by Type"
        )

        return fig

    def export_dashboard_report(self, format: str = 'json') -> str:
        """Export comprehensive dashboard report"""
        report = {
            'generated_at': datetime.now(),
            'overview': self.generate_market_overview(),
            'visualizations': self.create_dashboard_visualizations(),
            'recommendations': self._generate_recommendations(),
            'alerts': self._generate_alerts()
        }

        if format == 'json':
            return json.dumps(report, indent=2, default=str)
        else:
            # Could implement other formats like PDF, HTML, etc.
            return json.dumps(report, default=str)

    def _generate_recommendations(self) -> List[str]:
        """Generate AI-powered trading recommendations"""
        recommendations = []

        overview = self.generate_market_overview()

        # Market regime recommendations
        regime = overview.get('market_summary', {}).get('market_regime', 'unknown')
        if regime == 'strong_bull':
            recommendations.append("Consider increasing exposure to long positions in trending assets")
        elif regime == 'volatile':
            recommendations.append("Reduce position sizes and use wider stop losses")

        # Risk-based recommendations
        risk_level = overview.get('risk_assessment', {}).get('overall_risk', 'medium')
        if risk_level == 'high':
            recommendations.append("High risk environment - consider reducing portfolio leverage")
        elif risk_level == 'low':
            recommendations.append("Low risk environment - opportunity to increase position sizes")

        # Opportunity-based recommendations
        opportunities = overview.get('trading_opportunities', [])
        high_priority_opps = [opp for opp in opportunities if opp.get('priority') == 'high']
        if high_priority_opps:
            recommendations.append(f"Focus on {len(high_priority_opps)} high-priority trading opportunities")

        return recommendations if recommendations else ["Maintain current strategy - no significant changes recommended"]

    def _generate_alerts(self) -> List[Dict]:
        """Generate trading alerts based on AI analysis"""
        alerts = []

        if not self.dashboard_data:
            return alerts

        # Risk alerts
        risk_assessment = self.dashboard_data.get('market_summary', {}).get('risk_assessment', {})
        if risk_assessment.get('overall_risk') == 'high':
            alerts.append({
                'type': 'warning',
                'priority': 'high',
                'message': 'High market risk detected - consider reducing exposure',
                'timestamp': datetime.now()
            })

        # Opportunity alerts
        opportunities = self._identify_opportunities(self.dashboard_data.get('predictions', {}))
        urgent_opportunities = [opp for opp in opportunities if opp.get('confidence', 0) > 90]

        if urgent_opportunities:
            alerts.append({
                'type': 'opportunity',
                'priority': 'high',
                'message': f"{len(urgent_opportunities)} high-confidence trading opportunities detected",
                'timestamp': datetime.now()
            })

        # Performance alerts
        performance = self.dashboard_data.get('performance', {})
        if performance.get('win_rate', 0) < 0.4:
            alerts.append({
                'type': 'warning',
                'priority': 'medium',
                'message': 'Recent performance below threshold - review strategy parameters',
                'timestamp': datetime.now()
            })

        return alerts


class DashDashboard:
    """Interactive Dash-based dashboard"""

    def __init__(self, analytics_dashboard: PredictiveAnalyticsDashboard):
        self.analytics = analytics_dashboard
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

        self.app.layout = self.create_layout()
        self.setup_callbacks()

    def create_layout(self):
        """Create the dashboard layout"""
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("🚀 AI Predictive Analytics Dashboard",
                           className="text-center mb-4"),
                    html.P("Real-time AI insights and trading analytics",
                          className="text-center text-muted mb-4")
                ])
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Market Overview"),
                        dbc.CardBody([
                            html.Div(id='market-overview')
                        ])
                    ], className="mb-4")
                ], width=12)
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("AI Predictions Summary"),
                        dbc.CardBody([
                            html.Div(id='predictions-summary')
                        ])
                    ])
                ], width=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Risk Assessment"),
                        dbc.CardBody([
                            html.Div(id='risk-assessment')
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Key Insights"),
                        dbc.CardBody([
                            html.Div(id='key-insights')
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Trading Opportunities"),
                        dbc.CardBody([
                            html.Div(id='trading-opportunities')
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),

            # Charts section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Market Sentiment"),
                        dbc.CardBody([
                            dcc.Graph(id='sentiment-gauge')
                        ])
                    ])
                ], width=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("AI Confidence Timeline"),
                        dbc.CardBody([
                            dcc.Graph(id='confidence-chart')
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),

            # Refresh button
            dbc.Row([
                dbc.Col([
                    dbc.Button("Refresh Dashboard",
                             id='refresh-btn',
                             color='primary',
                             className="mb-4")
                ], className="text-center")
            ])
        ], fluid=True)

    def setup_callbacks(self):
        """Setup dashboard callbacks"""

        @self.app.callback(
            [Output('market-overview', 'children'),
             Output('predictions-summary', 'children'),
             Output('risk-assessment', 'children'),
             Output('key-insights', 'children'),
             Output('trading-opportunities', 'children'),
             Output('sentiment-gauge', 'figure'),
             Output('confidence-chart', 'figure')],
            [Input('refresh-btn', 'n_clicks')]
        )
        def update_dashboard(n_clicks):
            """Update all dashboard components"""

            try:
                overview = self.analytics.generate_market_overview()

                # Market overview
                market_overview = self._format_market_overview(overview)

                # Predictions summary
                predictions_summary = self._format_predictions_summary(overview)

                # Risk assessment
                risk_assessment = self._format_risk_assessment(overview)

                # Key insights
                key_insights = self._format_key_insights(overview)

                # Trading opportunities
                trading_opportunities = self._format_trading_opportunities(overview)

                # Charts
                sentiment_gauge = self.analytics._create_sentiment_gauge()
                confidence_chart = self.analytics._create_confidence_chart()

                return (market_overview, predictions_summary, risk_assessment,
                       key_insights, trading_opportunities, sentiment_gauge, confidence_chart)

            except Exception as e:
                error_msg = f"Error updating dashboard: {str(e)}"
                logger.error(error_msg)
                return (error_msg, "", "", "", "", go.Figure(), go.Figure())

    def _format_market_overview(self, overview: Dict) -> html.Div:
        """Format market overview for display"""
        market_summary = overview.get('market_summary', {})

        return html.Div([
            html.P(f"📊 Overall Sentiment: {market_summary.get('overall_sentiment', 'unknown').title()}"),
            html.P(f"📈 Market Regime: {market_summary.get('market_regime', 'unknown').replace('_', ' ').title()}"),
            html.P(f"🌊 Volatility Level: {market_summary.get('volatility_level', 'unknown').title()}"),
            html.P(f"📊 Assets Analyzed: {market_summary.get('assets_analyzed', 0)}")
        ])

    def _format_predictions_summary(self, overview: Dict) -> html.Div:
        """Format predictions summary"""
        predictions = overview.get('ai_predictions', {})

        return html.Div([
            html.P(f"🎯 Total Predictions: {predictions.get('total_predictions', 0)}"),
            html.P(f"📊 Average Confidence: {predictions.get('average_confidence', 0):.1f}%"),
            html.P(f"📈 Bullish Signals: {predictions.get('bullish_predictions', 0)}"),
            html.P(f"📉 Bearish Signals: {predictions.get('bearish_predictions', 0)}")
        ])

    def _format_risk_assessment(self, overview: Dict) -> html.Div:
        """Format risk assessment"""
        risk = overview.get('risk_assessment', {})

        return html.Div([
            html.P(f"⚠️ Overall Risk: {risk.get('overall_risk', 'unknown').title()}"),
            html.P(f"📊 Diversification Score: {risk.get('diversification_score', 0):.1f}/100"),
            html.P(f"🌊 Average Volatility: {risk.get('average_volatility', 0):.1%}"),
            html.Hr(),
            html.H6("Risk Factors:"),
            html.Ul([html.Li(factor) for factor in risk.get('risk_factors', [])])
        ])

    def _format_key_insights(self, overview: Dict) -> html.Div:
        """Format key insights"""
        insights = overview.get('key_insights', [])

        return html.Ul([html.Li(insight) for insight in insights])

    def _format_trading_opportunities(self, overview: Dict) -> html.Div:
        """Format trading opportunities"""
        opportunities = overview.get('trading_opportunities', [])

        if not opportunities:
            return html.P("No significant trading opportunities identified")

        opp_items = []
        for opp in opportunities[:5]:  # Show top 5
            priority_color = {'high': 'danger', 'medium': 'warning', 'low': 'info'}.get(opp.get('priority'), 'info')
            opp_items.append(
                dbc.Badge(
                    f"{opp.get('asset', 'Unknown')}: {opp.get('description', '')}",
                    color=priority_color,
                    className="mr-2 mb-2"
                )
            )

        return html.Div(opp_items)

    def run_server(self, debug: bool = False, port: int = 8050):
        """Run the dashboard server"""
        self.app.run_server(debug=debug, port=port)


if __name__ == "__main__":
    # Example usage
    dashboard = PredictiveAnalyticsDashboard()
    dash_app = DashDashboard(dashboard)

    print("AI Predictive Analytics Dashboard initialized!")
    print("Run dash_app.run_server() to start the interactive dashboard")
