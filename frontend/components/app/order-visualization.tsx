'use client';

import { useEffect, useState } from 'react';
import { useRoomContext } from '@livekit/components-react';
import { RoomEvent, DataPacket_Kind } from 'livekit-client';
import { motion, AnimatePresence } from 'motion/react';

interface OrderState {
    drinkType?: string;
    size?: string;
    milk?: string;
    extras?: string[];
    name?: string;
}

export function OrderVisualization() {
    const room = useRoomContext();
    const [order, setOrder] = useState<OrderState>({});

    useEffect(() => {
        const handleData = (payload: Uint8Array, participant: any, kind: DataPacket_Kind) => {
            try {
                const decoder = new TextDecoder();
                const str = decoder.decode(payload);
                const json = JSON.parse(str);
                if (json.type === 'order_update') {
                    console.log('Order update received:', json.data);
                    setOrder(json.data);
                }
            } catch (e) {
                console.error('Failed to parse data message', e);
            }
        };

        room.on(RoomEvent.DataReceived, handleData);
        return () => {
            room.off(RoomEvent.DataReceived, handleData);
        };
    }, [room]);

    // Visuals based on state
    const sizeScale = order.size === 'Small' ? 0.8 : order.size === 'Large' ? 1.4 : 1.0;
    const hasWhippedCream = order.extras?.some(e => e.toLowerCase().includes('whipped') || e.toLowerCase().includes('cream'));

    return (
        <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="fixed top-4 right-4 z-[100] p-6 bg-white rounded-xl shadow-2xl w-80 border-2 border-amber-600"
        >
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-xl text-amber-900">☕ Your Order</h3>
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" title="Live updates"></div>
            </div>

            <div className="flex flex-col items-center mb-6 h-32 justify-end bg-gradient-to-b from-amber-50 to-transparent rounded-lg p-4">
                {/* Cup Visualization */}
                <AnimatePresence>
                    <motion.div
                        className="relative"
                        animate={{ scale: sizeScale }}
                        transition={{ duration: 0.3 }}
                    >
                        {/* Cup Body */}
                        <div className="w-20 h-24 rounded-b-xl border-4 border-amber-800 bg-gradient-to-b from-amber-100 to-amber-200 overflow-hidden relative shadow-lg">
                            {/* Coffee Liquid */}
                            <motion.div
                                className="absolute bottom-0 w-full bg-gradient-to-t from-amber-900 to-amber-700"
                                initial={{ height: '0%' }}
                                animate={{ height: order.drinkType ? '75%' : '0%' }}
                                transition={{ duration: 0.5 }}
                            />
                            {/* Milk Layer */}
                            {order.milk && (
                                <motion.div
                                    className="absolute top-0 w-full h-1/4 bg-white/40"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ duration: 0.3 }}
                                />
                            )}
                        </div>

                        {/* Handle */}
                        <div className="absolute top-6 -right-4 w-5 h-10 border-4 border-amber-800 rounded-r-xl bg-gradient-to-r from-transparent to-amber-100"></div>

                        {/* Whipped Cream */}
                        {hasWhippedCream && (
                            <motion.div
                                initial={{ scale: 0, y: 10 }}
                                animate={{ scale: 1, y: 0 }}
                                className="absolute -top-5 left-0 w-20 h-8 bg-gradient-to-b from-white to-gray-100 rounded-full shadow-md border-2 border-gray-200"
                            />
                        )}
                    </motion.div>
                </AnimatePresence>
            </div>

            <div className="space-y-2 text-sm bg-amber-50 p-4 rounded-lg border border-amber-200">
                <div className="flex justify-between">
                    <span className="font-semibold text-amber-900">Name:</span>
                    <span className="text-gray-700">{order.name || '—'}</span>
                </div>
                <div className="flex justify-between">
                    <span className="font-semibold text-amber-900">Drink:</span>
                    <span className="text-gray-700">{order.drinkType || '—'}</span>
                </div>
                <div className="flex justify-between">
                    <span className="font-semibold text-amber-900">Size:</span>
                    <span className="text-gray-700">{order.size || '—'}</span>
                </div>
                <div className="flex justify-between">
                    <span className="font-semibold text-amber-900">Milk:</span>
                    <span className="text-gray-700">{order.milk || '—'}</span>
                </div>
                <div className="flex justify-between items-start">
                    <span className="font-semibold text-amber-900">Extras:</span>
                    <span className="text-gray-700 text-right">{order.extras && order.extras.length > 0 ? order.extras.join(', ') : '—'}</span>
                </div>
            </div>
        </motion.div>
    );
}
