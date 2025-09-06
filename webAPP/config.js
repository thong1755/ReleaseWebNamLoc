// Cấu hình URL API cho ứng dụng web
window.env = {
  apiBaseUrl: 'http://thongtestnamloc.duckdns.org:8000' // URL mặc định cho môi trường development
};

// Helper function để lấy image URL
window.getImageUrl = function(pictureType, dateStr, filename) {
  return `${window.env.apiBaseUrl}/picture/view/${pictureType}/${dateStr}/${filename}`;
};
