use crate::data::Types;
use anyhow::anyhow;
use pyo3::types::{PyDict, PyList};
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;
use crate::data::fields::field::Field;
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;

#[derive(Clone, Debug, Deserialize)]
pub struct UnionField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    pub variants: Vec<Field>,

    #[serde(skip, default)]
    pub active_variant: usize,
}

impl UnionField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        let mut success = false;
        let addr = state.reader.tell();
        for i in 0..self.variants.len() {
            // Attempt to read the current variant.
            self.variants[i].read(state)?;
            if self.variants[i].union_read_succeeded()? {
                // We got a value with this variant! Reading is done.
                success = true;
                self.active_variant = i;
                break;
            } else {
                // Rewind.
                state.reader.seek(addr);
            }
        }
        if !success {
            return Err(anyhow!("All variants failed to read for union {}", self.id));
        }
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        if self.active_variant > self.variants.len() {
            return Err(anyhow!("Variant out of range for union {}", self.id));
        }

        // Pass on the work to the active variant.
        self.variants[self.active_variant].write(state)
    }

    pub fn variant(&self) -> &Field {
        &self.variants[self.active_variant]
    }

    pub fn variant_mut(&mut self) -> &mut Field {
        &mut self.variants[self.active_variant]
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "union")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;

        let variants = PyList::empty(py);
        for variant in &self.variants {
            variants.append(variant.metadata(py)?)?;
        }
        dict.set_item("variants", variants)?;
        dict.set_item("active_variant", self.active_variant)?;

        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, _types: &mut Types) -> anyhow::Result<Field> {
        todo!()
    }
}