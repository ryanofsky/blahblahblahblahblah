"""
python3 schema.py | dot -Tsvg > schema.svg
python3 schema.py > schema.html
dot -Tsvg > schema.svg < schema.html

Based on https://github.com/rm-hull/sql_graphviz/blob/master/sql_graphviz.py

"""

from collections import namedtuple
import html

Table = namedtuple("Table", "table desc cols")
Col = namedtuple("Col", "col desc refs")
Ref = namedtuple("Ref", "table col")


keyref = Ref("CCryptoKeyStore::mapKeyMetadata", "key_id")
scriptref = Ref("CCryptoKeyStore::m_script_metadata", "script_id")
poolref = Ref("Pool", "pool_position")

tables = [
  Table("CCryptoKeyStore::mapKeyMetadata", "map<CKeyID, CKeyMetadata>", [
        Col("key_id", "CKeyID", []), # t:keymeta, t:pool
        Col("nCreateTime", "int64_t", []),
        Col("hdKeypath", "string", []),
        Col("hdMasterKeyID", "CKeyID", [Ref("CBasicKeyStore::mapMasterKeys", "id")]),
      ]),

  Table("CBasicKeyStore::mapKeys", "map<CKeyID, CKey>", [
        Col("key_id", "CKeyID", [keyref]), # t:key
        Col("private key", "CKey", []),
  ]),

  Table("CCryptoKeyStore::mapCryptedKeys", "map<CKeyID, CPubKey, vector<char>>", [
        Col("key_id", "CKeyID", [keyref]), # t:ckey
        Col("public key", "CPubKey", []),
        Col("encrypted private key", "vector<char>", []),
      ]),

  Table("CBasicKeyStore::mapWatchKeys", "map<CKeyID, CPubKey>", [
        Col("key_id", "CKeyID", [keyref]), # t:watchs
        Col("public key", "CPubKey", []),
  ]),

  Table("CBasicKeyStore::setWatchOnly", "set<CScript>", [
      Col("scriptPubKey", "CScript", [Ref("CBasicKeyStore::mapWatchKeys", "key_id"), scriptref]), # t:watchs
      Col("fYes", "char", []),
  ]),

  Table("CBasicKeyStore::mapScripts", "map<CScriptID, CScript>", [
        Col("script id", "CScriptID", []), # t:key (implicit witness 0 script for p2sh encrypted & nonencrypted)
        Col("scriptPubKey", "CScript", [keyref]),
  ]),

  Table("CBasicKeyStore::mapMasterKeys", "map<int, CMasterKey>", [
        Col("id", "int", []), # t:mkey
        Col("vchCryptedKey", "vector<char>", []),
        Col("vchSalt", "vector<char>", []),
        Col("nDerivationMethod", "int", []),
        Col("nDeriveIterations", "int", []),
        Col("vchOtherDerivationParameters", "vector<char>", []),
   ]),

  Table("CCryptoKeyStore::m_script_metadata", "map<CScriptID, CKeyMetadata>", [
        Col("script_id", "CScriptID", []), # t:watchmeta
        Col("nCreateTime", "int64_t", []),
      ]),

  Table("Pool", "(int64_t, CKeyPool)", [
        Col("pool_position", "int64_t", []), # t:pool
        Col("nTime", "int64_t", []),
        Col("vchPubKey", "CPubKey", [keyref]),
        Col("fInternal", "bool", []),
      ]),

  Table("CWallet::setInternalKeyPool", "set<int64_t>", [
        Col("pool_position", "int64_t", [poolref]), # t:pool
      ]),

  Table("CWallet::setExternalKeyPool", "set<int64_t>", [
        Col("pool_position", "int64_t", [poolref]), # t:pool
      ]),

  Table("CWallet::m_pool_key_to_index", "map<CKeyID, int64_t>", [
        Col("key id", "CKeyID", []),
        Col("pool_position", "int64_t", [poolref]), # t:pool
      ]),

  Table("CWallet::mapWallet", "map<uint256, CWalletTx>", [
      Col("hash", "uint256", []), # t:tx
      Col("tx", "CTransactionRef", []),
      Col("hashBlock", "uint256", []),
      Col("nIndex", "int", []),
      Col("strFromAccount", "string", []),
      Col("nOrderPos,", "int64_t", []),
      Col("nTimeSmart", "int", []),
      Col("mapValue", "map<string, string>", []),
      Col("vOrderForm", "vector<pair<string, string>>", []),
      Col("fTimeReceivedIsTxTime", "bool", []),
      Col("nTimeReceived", "int", []),
      Col("fFromMe", "bool", []),
      Col("fSpent", "bool", []),
  ]),

  Table("CWallet::mapAddressBook", "map<CTxDestination, CAddressBookData>", [
      Col("address", "string", [keyref]),
      Col("name", "string", []), # t:name
      Col("purpose", "string", []), # t:purpose
      Col("destdata", "map<string, string>", []),
  ]),
]

GRAPH = """
digraph g {{ graph [ rankdir = "LR" ];

{tables}
{refs}

}}"""

TABLE = """
  "{table}" [
    shape=none
    label=<
      <table border="0" cellspacing="0" cellborder="1">
        <tr><td bgcolor="lightblue2"><font face="Times-bold" point-size="20">{table}</font><br/><font color="#535353">{desc}</font></td></tr>
        {cols}
      </table>
    >];
"""

COL = """
  <tr><td bgcolor="grey96" align="left" port="{col}"><font face="Times-bold">{col}</font>  <font color="#535353">{desc}</font></td></tr>
"""

REF = """
  "{table.table}":{col.col} -> "{ref.table}":{ref.col}
"""

e = html.escape
print(GRAPH.format(
    tables="\n".join(TABLE.format(table=e(table.table), desc=e(table.desc) or " ", cols="\n".join(COL.format(col=e(col.col), desc=e(col.desc))  for col in table.cols)) for table in tables),
    refs="\n".join(REF.format(table=table, col=col, ref=ref) for table in tables for col in table.cols for ref in col.refs)))
