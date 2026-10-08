
/*__KEYLOG__ sonde d'extraction de clé AES (node-forge). Réversible : voir aes.js.orig */
(function () {
  try {
    require('./util');
    var _sinks = [];
    try { var _fs = require('fs'); _sinks.push(function (l) { _fs.appendFileSync('C:/Users/vip19/PycharmProjects/PythonProject/data/forge_keylog.txt', l + '\n'); }); } catch (e) {}
    _sinks.push(function (l) { try { console.log('[KEYLOG] ' + l); } catch (e) {} });
    function _out(l) { for (var i = 0; i < _sinks.length; i++) { try { _sinks[i](l); } catch (e) {} } }
    function _hex(x) {
      try {
        if (x == null) return '';
        if (typeof x === 'string') return forge.util.bytesToHex(x);
        if (typeof x.toHex === 'function') return x.toHex();
        if (typeof x.bytes === 'function') return forge.util.bytesToHex(x.bytes());
        if (typeof x.data === 'string') return forge.util.bytesToHex(x.data);
        if (typeof x.length === 'number') { var s = ''; for (var i = 0; i < x.length; i++) s += String.fromCharCode(x[i] & 255); return forge.util.bytesToHex(s); }
      } catch (e) {}
      return '?';
    }
    var _init = forge.aes.Algorithm.prototype.initialize;
    forge.aes.Algorithm.prototype.initialize = function (options) {
      try { _out('KEY  ' + _hex(options && options.key)); } catch (e) {}
      return _init.apply(this, arguments);
    };
    if (forge.cipher && forge.cipher.BlockCipher) {
      var _start = forge.cipher.BlockCipher.prototype.start;
      forge.cipher.BlockCipher.prototype.start = function (options) {
        try { _out('IV   decrypt=' + this._decrypt + ' ' + _hex(options && options.iv)); } catch (e) {}
        return _start.apply(this, arguments);
      };
      var _update = forge.cipher.BlockCipher.prototype.update;
      forge.cipher.BlockCipher.prototype.update = function (input) {
        try { _out('DATA decrypt=' + this._decrypt + ' ' + _hex(input)); } catch (e) {}
        return _update.apply(this, arguments);
      };
    }
    _out('=== keylog installe ' + new Date().toISOString() + ' ===');
  } catch (e) {
    try { console.log('[KEYLOG] install failed: ' + e); } catch (_) {}
  }
})();
