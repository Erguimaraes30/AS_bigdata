package com.example.api.controller;

import com.example.api.model.Matricula;
import com.example.api.model.MatriculaRequest;
import com.example.api.repository.MatriculaRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/matriculas")
public class MatriculaController {

    @Autowired
    private MatriculaRepository repository;

    @PostMapping
    public Matricula cadastrar(@RequestBody MatriculaRequest request) {
        Matricula matricula = new Matricula();
        matricula.setNome(request.getNome());
        matricula.setEmail(request.getEmail());
        matricula.setCurso(request.getCurso());
        return repository.save(matricula);
    }
}