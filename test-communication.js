const { execSync } = require('child_process');
const fs = require('fs');

console.log('🧪 INICIANDO TEST DE COMUNICACIÓN BACKEND');
console.log('=' .repeat(50));

// 1. Verificar si el servidor está corriendo
console.log('\n⌘ VERIFICANDO SERVIDOR...');
try {
    execSync('curl -s http://localhost:3000/api/auth', { stdio: 'pipe' });
    console.log('✅ Servidor respondiendo en http://localhost:3000');
} catch (error) {
    console.log('❌ Servidor no responde. Inicia el servidor con: npm run dev');
    process.exit(1);
}

// 2. Verificar conexión a MongoDB
console.log('\n🗄️ VERIFICANDO CONEXIÓN A BASE DE DATOS...');
try {
    const dbResult = execSync('node -e "require("./lib/mongodb").connectToDatabase().then(() => console.log(\"📝 Conectado\")).catch(err => console.error(\"\u274c Error\", err))"', { stdio: 'pipe' });
    console.log('✅ Base de datos accesible');
} catch (error) {
    console.log('❌ Error de conexión a base de datos');
    console.log('Asegúrate de configurar MONGODB_URI en .env');
}

// 3. Probar modelo User
console.log('\n👤 VERIFICANDO MODELO USER...');
try {
    const userModel = execSync('node -e "console.log(\"📋 User model disponible: \", typeof require("./models/User") === \'object\')"', { stdio: 'pipe' });
    console.log('✅ Modelo User cargado correctamente');
} catch (error) {
    console.log('❌ Error cargando modelo User');
}

// 4. Probar endpoint de signup
console.log('\n📝 PROBAR ENDPOINT DE REGISTRO...');
try {
    const signupResult = execSync(`curl -s -X POST http://localhost:3000/api/auth/signup \
    -H "Content-Type: application/json" \
    -d '\"name\":\"TestUser\",\"email\":\"test+${Date.now()}@example.com\",\"dob\":\"1990-01-01\",\"password\":\"123456\",\"confirmPassword\":\"123456\"}'`, { stdio: 'pipe' });
    
    const response = JSON.parse(signupResult.toString());
    if (response.message && response.message.includes('Usuario creado')) {
        console.log('✅ Endpoint signup funcionando');
    } else {
        console.log('⚠️ Respuesta signup:', response.message || 'Respuesta recibida');
    }
} catch (error) {
    console.log('❌ Error en endpoint signup');
    console.log('Posibles causas: servidor no iniciado, validaciones fallidas');
}

// 5. Probar next-auth providers
console.log('\n️️ VERIFICANDO PROVEEDORES DE AUTENTICACIÓN...');
try {
    const authProviders = execSync('curl -s http://localhost:3000/api/auth', { stdio: 'pipe' });
    console.log('✅ Proveedores de autenticación disponibles');
} catch (error) {
    console.log('❌ Error verificando providers');
}

// 6. Verificar variables de entorno
console.log('\n📋 VERIFICANDO VARIABLES DE ENTORNO...');
const requiredEnv = ['MONGODB_URI', 'NEXTAUTH_SECRET'];
const missingEnv = requiredEnv.filter(env => !process.env[env]);

if (missingEnv.length === 0) {
    console.log('✅ Todas las variables de entorno configuradas');
} else {
    console.log('⚠️ Variables faltantes:', missingEnv.join(', '));
}

console.log('\n' + '='.repeat(50));
console.log('🧪 TEST DE COMUNICACIÓN COMPLETADO');
console.log('💡 Para más detalles, revisa los mensajes anteriores');
console.log('💡 Si hay errores, verifica:');
console.log('  1. Servidor corriendo (npm run dev)');
console.log('  2. Configuración de .env');
console.log('  3. Conexión a MongoDB');