package com.bigdata.audiencias.model;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;

import java.io.IOException;

/**
 * Convierte los bytes JSON que publica el simulador (agentes-simulador) en
 * un objeto Event. El ObjectMapper se crea en open(), no en el constructor,
 * porque Jackson no es serializable y Flink puede mover esta clase entre
 * TaskManagers.
 */
public class EventDeserializer implements DeserializationSchema<Event> {

    private static final long serialVersionUID = 1L;

    private transient ObjectMapper objectMapper;

    @Override
    public void open(InitializationContext context) {
        this.objectMapper = new ObjectMapper();
    }

    @Override
    public Event deserialize(byte[] message) throws IOException {
        if (objectMapper == null) {
            objectMapper = new ObjectMapper();
        }
        return objectMapper.readValue(message, Event.class);
    }

    @Override
    public boolean isEndOfStream(Event nextElement) {
        return false; // stream infinito, nunca termina solo
    }

    @Override
    public TypeInformation<Event> getProducedType() {
        return TypeInformation.of(Event.class);
    }
}
