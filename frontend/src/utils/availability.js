export const toTime = (str) => {
    const [h, m] = str.split(':').map(Number);
    if ([h, m].some(Number.isNaN)) return null;
    if (h < 0 || h > 23 || m < 0 || m > 59) return null;
    return { h, m };
};

export const normalizeAvailability = (input) => {
    const [daysPart, hoursPart] = (input || '').split('|').map(s => s.trim());
    if (!daysPart || !hoursPart) throw new Error('Use format: MON,TUE|09:00-17:00');

    const days = daysPart
        .split(',')
        .map(d => d.trim().slice(0, 3).toUpperCase())
        .filter(Boolean);
    if (!days.length) throw new Error('At least one day is required');

    const [startRaw, endRaw] = hoursPart.split('-').map(s => s.trim());
    const start = toTime(startRaw);
    const end = toTime(endRaw);
    if (!start || !end) throw new Error('Time must be HH:MM (00-23)');
    if (start.h > end.h || (start.h === end.h && start.m >= end.m)) {
        throw new Error('End must be after start (same day)');
    }

    const pad = (n) => n.toString().padStart(2, '0');
    return `${days.join(',')}|${pad(start.h)}:${pad(start.m)}-${pad(end.h)}:${pad(end.m)}`;
};
