use std::collections::HashMap;

use anyhow::anyhow;
use mila::LayeredFilesystem;
use serde::Deserialize;

use crate::data::Types;
use crate::data::serialization::references::ReadReferences;
use crate::data::storage::table_inject_store::TableInjectStore;
use crate::data::storage::single_store::SingleStore;
use crate::data::storage::multi_store::MultiStore;
use crate::data::storage::asset_store::AssetStore;
use crate::model::read_output::ReadOutput;

#[derive(Deserialize, Debug)]
#[serde(rename_all = "snake_case", tag = "type")]
pub enum Store {
    Single(SingleStore),
    Multi(MultiStore),
    Asset(AssetStore),
    TableInject(TableInjectStore),
}

macro_rules! on_store {
    ($on:ident, $with:ident, $body:tt) => {
        match $on {
            Store::Single($with) => $body,
            Store::Asset($with) => $body,
            Store::Multi($with) => $body,
            Store::TableInject($with) => $body,
        }
    };
}

impl Store {
    pub fn dirty_files(&self) -> Vec<String> {
        on_store!(self, s, { s.dirty_files() })
    }

    pub fn set_filename(&mut self, filename: String) -> anyhow::Result<()> {
        match self {
            Store::Single(s) => s.set_filename(filename),
            Store::Asset(s) => s.set_filename(filename),
            Store::TableInject(s) => s.set_filename(filename),
            Store::Multi(_) => return Err(anyhow!("Unsupported operation.")),
        }
        Ok(())
    }

    pub fn id(&self) -> &str {
        on_store!(self, s, { &s.id })
    }

    pub fn read(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<ReadOutput> {
        match self {
            Store::Single(s) => s.read(types, references, fs),
            Store::Asset(s) => s.read(types, fs),
            Store::TableInject(s) => s.read(types, references, fs),
            Store::Multi(_) => Ok(ReadOutput::new()),
        }
    }

    pub fn write(
        &self,
        types: &Types,
        tables: &HashMap<String, (u64, String)>,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        match self {
            Store::Single(s) => s.write(types, tables, fs),
            Store::Asset(s) => s.write(types, fs),
            Store::TableInject(s) => s.write(types, tables, fs),
            Store::Multi(s) => s.write(types, tables, fs),
        }
    }

    pub fn is_dirty(&self) -> bool {
        match self {
            Store::Single(s) => s.dirty,
            Store::Asset(s) => s.dirty,
            Store::TableInject(s) => s.dirty,
            Store::Multi(s) => s.is_dirty(),
        }
    }

    pub fn set_dirty(&mut self, dirty: bool) -> anyhow::Result<()> {
        match self {
            Store::Single(s) => s.dirty = dirty,
            Store::Asset(s) => s.dirty = dirty,
            Store::TableInject(s) => s.dirty = dirty,
            Store::Multi(_) => {
                return Err(anyhow!(
                    "Cannot mark a multi as dirty. Mark individual keys instead."
                ));
            }
        }
        Ok(())
    }
}