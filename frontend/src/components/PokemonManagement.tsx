import React, { useState } from 'react';
import { Download, List, Sparkles, Search } from 'lucide-react';
import { Card, CardHeader, CardContent } from './ui/Card';
import { LoadingButton } from './ui/Loading';
import { useImportPokemon, usePokemons } from '../hooks/useApi';
import type { Pokemon } from '../types/api';

interface PokemonCardProps {
  pokemon: Pokemon;
}

const PokemonCard: React.FC<PokemonCardProps> = ({ pokemon }) => {
  return (
    <div className="pokemon-card">
      <img
        src={pokemon.sprites.front_default || '/placeholder.svg'}
        alt={pokemon.name}
        className="w-20 h-20 mx-auto mb-2 object-contain"
      />
      <h6 className="font-semibold capitalize">{pokemon.name}</h6>
      <small className="text-gray-500">ID: {pokemon.id}</small>
      <div className="mt-2 flex flex-wrap justify-center gap-1">
        {pokemon.types.map((type, index) => (
          <span
            key={index}
            className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded-full"
          >
            {type.name}
          </span>
        ))}
      </div>
    </div>
  );
};

export const PokemonManagement: React.FC = () => {
  const [pokemonName, setPokemonName] = useState('');
  const [showList, setShowList] = useState(false);
  
  const importMutation = useImportPokemon();
  const { data: pokemonsData, isLoading: pokemonsLoading, refetch } = usePokemons(0, 20);

  const handleImport = () => {
    if (!pokemonName.trim()) {
      return;
    }
    importMutation.mutate(pokemonName.trim().toLowerCase());
    setPokemonName('');
  };

  const handleImportSamples = () => {
    const samples = ['pikachu', 'charizard', 'blastoise', 'venusaur', 'alakazam'];
    samples.forEach((pokemon, index) => {
      setTimeout(() => {
        importMutation.mutate(pokemon);
      }, index * 1000); // Delay to avoid overwhelming the API
    });
  };

  const handleListPokemons = () => {
    setShowList(true);
    refetch();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleImport();
    }
  };

  return (
    <Card>
      <CardHeader>
        <h5 className="text-lg font-semibold flex items-center">
          <Download className="w-5 h-5 mr-2" />
          Gerenciar Pokémons
        </h5>
      </CardHeader>
      
      <CardContent>
        {/* Import Section */}
        <div className="space-y-4">
          <div className="flex gap-2">
            <div className="flex-1">
              <input
                type="text"
                value={pokemonName}
                onChange={(e) => setPokemonName(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Nome do pokémon"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <LoadingButton
              isLoading={importMutation.isPending}
              onClick={handleImport}
              disabled={!pokemonName.trim()}
              className="btn-primary"
            >
              <Download className="w-4 h-4 mr-2" />
              Importar
            </LoadingButton>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-2">
            <LoadingButton
              isLoading={importMutation.isPending}
              onClick={handleImportSamples}
              className="btn-secondary btn-sm"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Importar Exemplos
            </LoadingButton>
            
            <LoadingButton
              isLoading={pokemonsLoading}
              onClick={handleListPokemons}
              className="btn-secondary btn-sm"
            >
              <List className="w-4 h-4 mr-2" />
              Listar Todos
            </LoadingButton>
          </div>
        </div>

        {/* Pokemon List */}
        {showList && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <h6 className="font-semibold flex items-center">
                <Search className="w-4 h-4 mr-2" />
                Pokémons Cadastrados
              </h6>
              {pokemonsData && (
                <span className="text-sm text-gray-500">
                  Total: {pokemonsData.total}
                </span>
              )}
            </div>
            
            {pokemonsLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                <p className="mt-2 text-gray-500">Carregando pokémons...</p>
              </div>
            ) : pokemonsData?.data && pokemonsData.data.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {pokemonsData.data.map((pokemon) => (
                  <PokemonCard key={pokemon.id} pokemon={pokemon} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                Nenhum pokémon encontrado
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
