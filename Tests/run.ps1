# TESTS DESCRIPTION
#python main.py --help

# TESTS WITHOUT BLOCKCHAIN

# python main.py --help
 #python main.py --type authentication --authentication-url http://localhost:5000/ --jwt-secret JWT_SECRET_KEY --roles-field roles --owner-role vlasnik --customer-role kupac --courier-role kurir
 #python main.py --type level0 --with-authentication --authentication-url http://localhost:5000 --owner-url http://localhost:5001 --customer-url http://localhost:5003
 #python main.py --type level1 --with-authentication --authentication-url http://localhost:5000 --owner-url http://localhost:5001 --customer-url http://localhost:5003
#python main.py --type level2 --with-authentication --authentication-url http://localhost:5000 --owner-url http://localhost:5001 --customer-url http://localhost:5003 --courier-url http://localhost:5002
#python main.py --type level3 --with-authentication --authentication-url http://localhost:5000 --owner-url http://localhost:5001 --customer-url http://localhost:5003 --courier-url http://localhost:5002
#python main.py --type all --authentication-url http://localhost:5000  --jwt-secret JWT_SECRET_KEY --roles-field roles --owner-role vlasnik --customer-role kupac --courier-role kurir --with-authentication --owner-url http://localhost:5001 --customer-url http://localhost:5003 --courier-url http://localhost:5002

# TESTS WITH BLOCKCHAIN

python .\initialize_customer_account.py

# python main.py --type level1 --with-authentication --authentication-url http://127.0.0.1:5000 --owner-url http://127.0.0.1:5001 --customer-url http://127.0.0.1:5002 --with-blockchain --provider-url http://127.0.0.1:8545 --customer-keys-path ./keys.json --customer-passphrase iep_project --owner-private-key 0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60
#python main.py --type level2 --with-authentication --authentication-url http://localhost:5000 --owner-url http://localhost:5001 --customer-url http://localhost:5003 --courier-url http://localhost:5002 --with-blockchain --provider-url http://localhost:8545 --customer-keys-path ./keys.json --customer-passphrase iep_project --owner-private-key 0x1f4ca9a90ce0b815664a02708ad9214954482a8fd8bc22975bbc18c1c17f3f2d --courier-private-key 0x6f434dc7dba60f67e226f509d3f3e71532b52732a97a3de35466961571b293e9
# python main.py --type level3 --with-authentication --authentication-url http://127.0.0.1:5000 --owner-url http://127.0.0.1:5001 --customer-url http://127.0.0.1:5002 --courier-url http://127.0.0.1:5003 --with-blockchain --provider-url http://127.0.0.1:8545 --customer-keys-path ./keys.json --customer-passphrase iep_project --owner-private-key 0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60 --courier-private-key 0xbe07088da4ecd73ecb3d9d806cf391dfaef5f15f9ee131265da8af81728a4379
python main.py --type all --authentication-url http://localhost:5000 --jwt-secret JWT_SECRET_KEY --roles-field roles --owner-role vlasnik --customer-role kupac --courier-role kurir --with-authentication --owner-url http://localhost:5001  --customer-url http://localhost:5003  --courier-url http://localhost:5002 --with-blockchain --provider-url http://localhost:8545 --customer-keys-path ./keys.json --customer-passphrase iep_project --owner-private-key 0x4aa7c8ab7227a212a6653f798f72ba7651e710923d1a44adbd179f533f3e688a --courier-private-key 0xc7ce105071c4e19d918e7744cffdb9bdcfc6e6fd1bc914e0550fffcc17c29fbb